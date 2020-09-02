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
from typing import Any, List, Optional

router = APIRouter()


class AccumulateTallyRequest(BaseModel):
    ballots: List[Any]
    encrypted_tally: Optional[Any] = None
    description: Any
    context: Any


@router.post("/accumulate")
def accumulate_tally(request: AccumulateTallyRequest = Body(...)) -> Any:
    """
    Accumulate ballots into a new or existing tally
    """

    ballots = [
        CiphertextAcceptedBallot.from_json_object(ballot) for ballot in request.ballots
    ]
    description = ElectionDescription.from_json_object(request.description)
    internal_description = InternalElectionDescription(description)
    context = CiphertextElectionContext.from_json_object(request.context)
    published_tally: Optional[PublishedCiphertextTally] = (
        PublishedCiphertextTally.from_json_object(request.encrypted_tally)
        if request.encrypted_tally
        else None
    )

    tally = _get_new_or_existing_tally(internal_description, context, published_tally)

    tally_succeeded = tally.batch_append(ballots)

    if tally_succeeded:
        published_tally = publish_ciphertext_tally(tally)
        return published_tally.to_json_object()
    else:
        raise HTTPException(
            status_code=500, detail="Tally accumulation was unsuccessful"
        )


def _get_new_or_existing_tally(
    description: ElectionDescription,
    context: CiphertextElectionContext,
    published_tally: PublishedCiphertextTally,
) -> CiphertextTally:
    if not published_tally:
        return CiphertextTally("election-results", description, context)

    full_tally = CiphertextTally(published_tally.object_id, description, context)
    full_tally.cast = published_tally.cast

    return full_tally
