from typing import Any, Dict, List, Optional
from electionguard.ballot import (
    SubmittedBallot,
    CiphertextBallot,
    PlaintextBallot,
)
from electionguard.ballot_box import accept_ballot, BallotBoxState
from electionguard.decrypt_with_shares import decrypt_ballot
from electionguard.decryption_share import DecryptionShare
from electionguard.data_store import DataStore
from electionguard.election import CiphertextElectionContext
from electionguard.manifest import InternalManifest, Manifest
from electionguard.encrypt import encrypt_ballot
from electionguard.group import ElementModQ
from electionguard.serializable import read_json_object, write_json_object
from electionguard.types import BALLOT_ID, GUARDIAN_ID
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
        SubmittedBallot.from_json_object(ballot) for ballot in request.encrypted_ballots
    ]
    context: CiphertextElectionContext = CiphertextElectionContext.from_json_object(
        request.context
    )

    all_shares: List[DecryptionShare] = [
        read_json_object(share, DecryptionShare)
        for shares in request.shares.values()
        for share in shares
    ]
    shares_by_ballot = index_shares_by_ballot(all_shares)

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
    description = InternalManifest(Manifest.from_json_object(request.description))
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
        current_hash = get_optional(encrypted_ballot.crypto_hash)

    response = EncryptBallotsResponse(
        encrypted_ballots=[ballot.to_json_object() for ballot in encrypted_ballots],
        next_seed_hash=write_json_object(current_hash),
    )
    return response


def handle_ballot(request: AcceptBallotRequest, state: BallotBoxState) -> Any:
    ballot = CiphertextBallot.from_json_object(request.ballot)
    description = Manifest.from_json_object(request.description)
    internal_description = InternalManifest(description)
    context = CiphertextElectionContext.from_json_object(request.context)

    accepted_ballot = accept_ballot(
        ballot,
        state,
        internal_description,
        context,
        DataStore(),
    )

    return accepted_ballot


def index_shares_by_ballot(
    shares: List[DecryptionShare],
) -> Dict[BALLOT_ID, Dict[GUARDIAN_ID, DecryptionShare]]:
    """
    Construct a lookup by ballot ID containing the dictionary of shares needed
    to decrypt that ballot.
    """
    shares_by_ballot: Dict[str, Dict[str, DecryptionShare]] = {}
    for share in shares:
        ballot_shares = shares_by_ballot.setdefault(share.object_id, {})
        ballot_shares[share.guardian_id] = share

    return shares_by_ballot
