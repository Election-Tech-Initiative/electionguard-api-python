from typing import Any
from electionguard.ballot import CiphertextAcceptedBallot
from electionguard.decryption import compute_decryption_share_for_ballot
from electionguard.election import CiphertextElectionContext
from electionguard.scheduler import Scheduler
from electionguard.serializable import write_json_object
from fastapi import APIRouter, Body, Depends

from app.core.scheduler import get_scheduler
from ..models import (
    convert_guardian,
    DecryptBallotSharesRequest,
    DecryptBallotSharesResponse,
)
from ..tags import TALLY

router = APIRouter()


@router.post("/decrypt-shares", tags=[TALLY])
def decrypt_ballot_shares(
    request: DecryptBallotSharesRequest = Body(...),
    scheduler: Scheduler = Depends(get_scheduler),
) -> Any:
    """
    Decrypt this guardian's share of one or more ballots
    """
    ballots = [
        CiphertextAcceptedBallot.from_json_object(ballot)
        for ballot in request.encrypted_ballots
    ]
    context = CiphertextElectionContext.from_json_object(request.context)
    guardian = convert_guardian(request.guardian)

    shares = [
        compute_decryption_share_for_ballot(guardian, ballot, context, scheduler)
        for ballot in ballots
    ]

    response = DecryptBallotSharesResponse(
        shares=[write_json_object(share) for share in shares]
    )

    return response
