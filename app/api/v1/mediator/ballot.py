from electionguard.ballot import CiphertextBallot, PlaintextBallot
from electionguard.ballot_box import accept_ballot, BallotBoxState
from electionguard.ballot_store import BallotStore
from electionguard.election import (
    CiphertextElectionContext,
    ElectionDescription,
    InternalElectionDescription,
)
from electionguard.encrypt import encrypt_ballot
from electionguard.group import ElementModQ
from electionguard.serializable import write_json_object
from electionguard.utils import get_optional
from fastapi import APIRouter, Body, HTTPException
from typing import Any, Optional

from app.utils.serialize import read_json_object
from ..models import AcceptBallotRequest, EncryptBallotsRequest, EncryptBallotsResponse
from ..tags import CAST_AND_SPOIL, ENCRYPT_BALLOTS

router = APIRouter()


@router.post("/cast", tags=[CAST_AND_SPOIL])
def cast_ballot(request: AcceptBallotRequest = Body(...)) -> Any:
    """
    Cast ballot
    """
    cast_ballot = handle_ballot(request, BallotBoxState.CAST)
    if not cast_ballot:
        raise HTTPException(
            status_code=500,
            detail="Ballot failed to be cast",
        )
    return cast_ballot.to_json_object()


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
        tracking_hash=write_json_object(current_hash),
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
