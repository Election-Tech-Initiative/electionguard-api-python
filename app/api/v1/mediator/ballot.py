from electionguard.ballot import CiphertextBallot
from electionguard.ballot_box import accept_ballot, BallotBoxState
from electionguard.election import (
    CiphertextElectionContext,
    ElectionDescription,
    InternalElectionDescription,
)
from electionguard.ballot_store import BallotStore
from fastapi import APIRouter, Body, HTTPException
from typing import Any

from ..models import AcceptBallotRequest
from ..tags import CAST_AND_SPOIL

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
