from electionguard.ballot import CiphertextAcceptedBallot
from electionguard.decryption import compute_decryption_share_for_ballot
from electionguard.election import CiphertextElectionContext
from electionguard.scheduler import Scheduler
from electionguard.serializable import write_json_object
from fastapi import APIRouter, Body
from typing import Any

from ..models import (
    convert_guardian,
    DecryptBallotSharesRequest,
    DecryptBallotSharesResponse,
)
from ..tags import TALLY

router = APIRouter()


@router.post("/decrypt-share", tags=[TALLY])
def decrypt_ballot_shares(request: DecryptBallotSharesRequest = Body(...)) -> Any:
    """
    Decrypt this guardian's share of one or more ballots
    """
    ballots = [
        CiphertextAcceptedBallot.from_json_object(ballot)
        for ballot in request.encrypted_ballots
    ]
    context = CiphertextElectionContext.from_json_object(request.context)
    guardian = convert_guardian(request.guardian)

    scheduler = Scheduler()
    shares = [
        compute_decryption_share_for_ballot(guardian, ballot, context, scheduler)
        for ballot in ballots
    ]

    response = DecryptBallotSharesResponse(
        shares=[write_json_object(share) for share in shares]
    )

    return response
