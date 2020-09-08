from electionguard.ballot import CiphertextAcceptedBallot
from electionguard.election import (
    CiphertextElectionContext,
    ElectionDescription,
    InternalElectionDescription,
)
from electionguard.tally import (
    publish_ciphertext_tally,
    CiphertextTally,
    PublishedCiphertextTally,
)
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import Any, List, Tuple

router = APIRouter()


class StartTallyRequest(BaseModel):
    ballots: List[Any]
    description: Any
    context: Any


class AppendTallyRequest(StartTallyRequest):
    encrypted_tally: Any


@router.post("")
def start_tally(request: StartTallyRequest = Body(...)) -> Any:
    """
    Start a new tally of a collection of ballots
    """

    ballots, description, context = parse_request(request)
    tally = CiphertextTally("election-results", description, context)

    return tally_ballots(tally, ballots)


@router.post("/append")
def append_to_tally(request: AppendTallyRequest = Body(...)) -> Any:
    """
    Append ballots into an existing tally
    """

    ballots, description, context = parse_request(request)

    published_tally = PublishedCiphertextTally.from_json_object(request.encrypted_tally)
    tally = CiphertextTally(published_tally.object_id, description, context)
    tally.cast = published_tally.cast

    return tally_ballots(tally, ballots)


def parse_request(
    request: StartTallyRequest,
) -> Tuple[
    List[CiphertextAcceptedBallot],
    InternalElectionDescription,
    CiphertextElectionContext,
]:
    """
    Deserialize common tally request values
    """
    ballots = [
        CiphertextAcceptedBallot.from_json_object(ballot) for ballot in request.ballots
    ]
    description = ElectionDescription.from_json_object(request.description)
    internal_description = InternalElectionDescription(description)
    context = CiphertextElectionContext.from_json_object(request.context)

    return (ballots, internal_description, context)


def tally_ballots(
    tally: CiphertextTally, ballots: List[CiphertextAcceptedBallot]
) -> PublishedCiphertextTally:
    tally_succeeded = tally.batch_append(ballots)

    if tally_succeeded:
        published_tally = publish_ciphertext_tally(tally)
        return published_tally.to_json_object()
    else:
        raise HTTPException(status_code=500, detail="Unable to tally ballots")
