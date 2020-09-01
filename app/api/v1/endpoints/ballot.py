from electionguard.ballot import CiphertextBallot
from electionguard.ballot_box import accept_ballot, BallotBoxState
from electionguard.election import (
    CiphertextElectionContext,
    ElectionDescription,
    InternalElectionDescription,
)
from electionguard.ballot_store import BallotStore
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import Any
from app.utils.serialize import write_json, write_json_object

router = APIRouter()


class AcceptBallotRequest(BaseModel):
    ballot: Any
    description: Any
    context: Any


@router.post("/cast")
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
    return write_json_object(cast_ballot)


@router.post("/spoil")
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
    return write_json_object(spoiled_ballot)


def handle_ballot(request: AcceptBallotRequest, state: BallotBoxState) -> Any:
    ballot = CiphertextBallot.from_json(write_json(request.ballot))
    description = ElectionDescription.from_json(write_json(request.description))
    internal_description = InternalElectionDescription(description)
    context = CiphertextElectionContext.from_json(write_json(request.context))

    accepted_ballot = accept_ballot(
        ballot,
        state,
        internal_description,
        context,
        BallotStore(),
    )

    return accepted_ballot
