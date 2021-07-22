from electionguard.ballot import SubmittedBallot
from electionguard.decryption import compute_decryption_share_for_ballot
from electionguard.election import CiphertextElectionContext
from electionguard.key_ceremony import ElectionKeyPair
from electionguard.scheduler import Scheduler
from electionguard.serializable import read_json_object, write_json_object
from fastapi import APIRouter, Body, Depends

from app.core.scheduler import get_scheduler
from ..models import (
    DecryptBallotSharesRequest,
    DecryptBallotSharesResponse,
)
from ..tags import TALLY

router = APIRouter()


@router.post(
    "/decrypt-shares", response_model=DecryptBallotSharesResponse, tags=[TALLY]
)
def decrypt_ballot_shares(
    request: DecryptBallotSharesRequest = Body(...),
    scheduler: Scheduler = Depends(get_scheduler),
) -> DecryptBallotSharesResponse:
    """
    Decrypt this guardian's share of one or more ballots
    """
    ballots = [
        SubmittedBallot.from_json_object(ballot) for ballot in request.encrypted_ballots
    ]
    context = CiphertextElectionContext.from_json_object(request.context)
    election_key_pair = read_json_object(
        request.guardian.election_keys, ElectionKeyPair
    )

    shares = [
        compute_decryption_share_for_ballot(
            election_key_pair, ballot, context, scheduler
        )
        for ballot in ballots
    ]

    response = DecryptBallotSharesResponse(
        shares=[write_json_object(share) for share in shares]
    )

    return response
