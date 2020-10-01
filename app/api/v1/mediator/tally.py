from typing import Any, List, Tuple
from electionguard.ballot import CiphertextAcceptedBallot
from electionguard.decrypt_with_shares import decrypt_tally as decrypt
from electionguard.decryption_share import TallyDecryptionShare
from electionguard.election import (
    CiphertextElectionContext,
    ElectionDescription,
    InternalElectionDescription,
)
from electionguard.scheduler import Scheduler
from electionguard.serializable import read_json_object
from electionguard.tally import (
    publish_ciphertext_tally,
    publish_plaintext_tally,
    CiphertextTally,
)
from fastapi import APIRouter, Body, Depends, HTTPException

from app.core.scheduler import get_scheduler
from ..models import (
    convert_tally,
    AppendTallyRequest,
    DecryptTallyRequest,
    StartTallyRequest,
)
from ..tags import TALLY


router = APIRouter()


@router.post("", tags=[TALLY])
def start_tally(
    request: StartTallyRequest = Body(...),
    scheduler: Scheduler = Depends(get_scheduler),
) -> Any:
    """
    Start a new tally of a collection of ballots
    """

    ballots, description, context = _parse_tally_request(request)
    tally = CiphertextTally("election-results", description, context)

    return _tally_ballots(tally, ballots, scheduler)


@router.post("/append", tags=[TALLY])
def append_to_tally(
    request: AppendTallyRequest = Body(...),
    scheduler: Scheduler = Depends(get_scheduler),
) -> Any:
    """
    Append ballots into an existing tally
    """

    ballots, description, context = _parse_tally_request(request)
    tally = convert_tally(request.encrypted_tally, description, context)

    return _tally_ballots(tally, ballots, scheduler)


@router.post("/decrypt", tags=[TALLY])
def decrypt_tally(request: DecryptTallyRequest = Body(...)) -> Any:
    """
    Decrypt a tally from a collection of decrypted guardian shares
    """
    description = InternalElectionDescription(
        ElectionDescription.from_json_object(request.description)
    )
    context = CiphertextElectionContext.from_json_object(request.context)
    tally = convert_tally(request.encrypted_tally, description, context)

    shares = {
        guardian_id: read_json_object(share, TallyDecryptionShare)
        for guardian_id, share in request.shares.items()
    }

    full_plaintext_tally = decrypt(tally, shares, context)
    if not full_plaintext_tally:
        raise HTTPException(
            status_code=500,
            detail="Unable to decrypt tally",
        )
    published_plaintext_tally = publish_plaintext_tally(full_plaintext_tally)

    return published_plaintext_tally.to_json_object()


def _parse_tally_request(
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


def _tally_ballots(
    tally: CiphertextTally,
    ballots: List[CiphertextAcceptedBallot],
    scheduler: Scheduler,
) -> Any:
    """
    Append a series of ballots to a new or existing tally
    """
    tally_succeeded = tally.batch_append(ballots, scheduler)

    if tally_succeeded:
        published_tally = publish_ciphertext_tally(tally)
        return published_tally.to_json_object()
    raise HTTPException(status_code=500, detail="Unable to tally ballots")
