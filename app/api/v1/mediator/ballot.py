from typing import Any, Dict, List, Optional
from electionguard.ballot import (
    CiphertextAcceptedBallot,
    CiphertextBallot,
    PlaintextBallot,
)
from electionguard.ballot_box import accept_ballot, BallotBoxState
from electionguard.decrypt_with_shares import decrypt_ballot
from electionguard.decryption_share import BallotDecryptionShare
from electionguard.ballot_store import BallotStore
from electionguard.election import (
    CiphertextElectionContext,
    ElectionDescription,
    InternalElectionDescription,
)
from electionguard.encrypt import encrypt_ballot
from electionguard.group import ElementModQ
from electionguard.serializable import read_json_object, write_json_object
from electionguard.utils import get_optional
from fastapi import APIRouter, Body, HTTPException

from ..models import (
    AcceptBallotRequest,
    DecryptBallotsRequest,
    EncryptBallotsRequest,
    EncryptBallotsResponse,
)
from ..tags import CAST_AND_SPOIL, ENCRYPT_BALLOTS, TALLY

router = APIRouter()


@router.post("/cast", tags=[CAST_AND_SPOIL])
def cast_ballot(request: AcceptBallotRequest = Body(...)) -> Any:
    """
    Cast ballot
    """
    casted_ballot = handle_ballot(request, BallotBoxState.CAST)
    if not casted_ballot:
        raise HTTPException(
            status_code=500,
            detail="Ballot failed to be cast",
        )
    return casted_ballot.to_json_object()


@router.post("/decrypt", tags=[TALLY])
def decrypt_ballots(request: DecryptBallotsRequest = Body(...)) -> Any:
    ballots = [
        CiphertextAcceptedBallot.from_json_object(ballot)
        for ballot in request.encrypted_ballots
    ]
    context: CiphertextElectionContext = CiphertextElectionContext.from_json_object(
        request.context
    )

    # Build a lookup for each ballot, containing the shares for decryption
    all_shares: List[BallotDecryptionShare] = [
        read_json_object(share, BallotDecryptionShare)
        for shares in request.shares.values()
        for share in shares
    ]
    shares_by_ballot: Dict[str, Dict[str, BallotDecryptionShare]] = {}
    for share in all_shares:
        ballot_shares = shares_by_ballot.setdefault(share.ballot_id, {})
        ballot_shares[share.guardian_id] = share

    extended_base_hash = context.crypto_extended_base_hash
    decrypted_ballots = {
        ballot.object_id: decrypt_ballot(
            ballot, shares_by_ballot[ballot.object_id], extended_base_hash
        )
        for ballot in ballots
    }

    return write_json_object(decrypted_ballots)


@router.post("/spoil", tags=[CAST_AND_SPOIL])
def spoil_ballot(request: AcceptBallotRequest = Body(...)) -> Any:
    """
    Spoil ballot
    """
    spoiled_ballot = handle_ballot(request, BallotBoxState.SPOILED)
    if not spoiled_ballot:
        raise HTTPException(
            status_code=500,
            detail="Ballot failed to be spoiled",
        )
    return spoiled_ballot.to_json_object()


@router.post("/encrypt", tags=[ENCRYPT_BALLOTS])
def encrypt_ballots(request: EncryptBallotsRequest = Body(...)) -> Any:
    """
    Encrypt one or more ballots
    """
    ballots = [PlaintextBallot.from_json_object(ballot) for ballot in request.ballots]
    description = InternalElectionDescription(
        ElectionDescription.from_json_object(request.description)
    )
    context = CiphertextElectionContext.from_json_object(request.context)
    seed_hash = read_json_object(request.seed_hash, ElementModQ)
    nonce: Optional[ElementModQ] = (
        read_json_object(request.nonce, ElementModQ) if request.nonce else None
    )

    encrypted_ballots = []
    current_hash = seed_hash

    for ballot in ballots:
        encrypted_ballot = encrypt_ballot(
            ballot, description, context, current_hash, nonce
        )
        if not encrypted_ballot:
            raise HTTPException(status_code=500, detail="Ballot failed to encrypt")
        encrypted_ballots.append(encrypted_ballot)
        current_hash = get_optional(encrypted_ballot.tracking_hash)

    response = EncryptBallotsResponse(
        encrypted_ballots=[ballot.to_json_object() for ballot in encrypted_ballots],
        next_seed_hash=write_json_object(current_hash),
    )
    return response


def handle_ballot(request: AcceptBallotRequest, state: BallotBoxState) -> Any:
    ballot = CiphertextBallot.from_json_object(request.ballot)
    description = ElectionDescription.from_json_object(request.description)
    internal_description = InternalElectionDescription(description)
    context = CiphertextElectionContext.from_json_object(request.context)

    accepted_ballot = accept_ballot(
        ballot,
        state,
        internal_description,
        context,
        BallotStore(),
    )

    return accepted_ballot
