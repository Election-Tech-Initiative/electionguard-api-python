from fastapi import APIRouter, Body, HTTPException, Request, status

import electionguard.tally

from electionguard.key_ceremony import PublicKeySet
from electionguard.election import CiphertextElectionContext
from electionguard.decryption_share import DecryptionShare
from electionguard.serializable import read_json_object
from electionguard.tally import CiphertextTallyContest
from electionguard.utils import get_optional

from app.core.election import get_election
from app.core.key_guardian import get_key_guardian
from app.core.tally import get_ciphertext_tally
from app.core.tally_decrypt import (
    get_decryption_share,
    set_decryption_share,
    filter_decryption_shares,
)
from ..models import (
    BaseResponse,
    DecryptionShareResponse,
    BaseQueryRequest,
    DecryptionShareRequest,
)
from ..tags import TALLY_DECRYPT


router = APIRouter()


@router.get("", response_model=DecryptionShareResponse, tags=[TALLY_DECRYPT])
def fetch_decryption_share(
    request: Request, election_id: str, tally_name: str, guardian_id: str
) -> DecryptionShareResponse:
    """Get a decryption share for a specific tally for a specific guardian."""
    share = get_decryption_share(
        election_id, tally_name, guardian_id, request.app.state.settings
    )
    return DecryptionShareResponse(
        shares=[share],
    )


@router.post("/submit-share", response_model=BaseResponse, tags=[TALLY_DECRYPT])
def submit_share(
    request: Request,
    data: DecryptionShareRequest = Body(...),
) -> BaseResponse:
    """
    Announce a guardian participating in a tally decryption by submitting a decryption share.
    """

    election = get_election(data.share.election_id, request.app.state.settings)
    context = CiphertextElectionContext.from_json_object(election.context)
    guardian = get_key_guardian(
        election.key_name, data.share.guardian_id, request.app.state.settings
    )
    public_keys = read_json_object(get_optional(guardian.public_keys), PublicKeySet)

    api_tally = get_ciphertext_tally(
        data.share.election_id, data.share.tally_name, request.app.state.settings
    )
    tally_share = read_json_object(data.share.tally_share, DecryptionShare)

    # TODO: spoiled ballot shares
    # ballot_shares = [
    #     read_json_object(ballot_share, DecryptionShare)
    #     for ballot_share in data.share.ballot_shares
    # ]

    # validate the decryption share data matches the expectations in the tally
    # TODO: use the SDK for validation
    # sdk_tally = read_json_object(api_tally.tally, electionguard.tally.CiphertextTally)
    for contest_id, contest in api_tally.tally["contests"].items():
        tally_contest = read_json_object(contest, CiphertextTallyContest)
        contest_share = tally_share.contests[contest_id]
        for selection_id, selection in tally_contest.selections.items():
            selection_share = contest_share.selections[selection_id]
            if not selection_share.is_valid(
                selection.ciphertext,
                public_keys.election.key,
                context.crypto_extended_base_hash,
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"decryption share failed valitation for contest: {contest_id} selection: {selection_id}",
                )

    # TODO: validate spoiled ballot shares

    return set_decryption_share(data.share, request.app.state.settings)


@router.get("/find", response_model=DecryptionShareResponse, tags=[TALLY_DECRYPT])
def find_decryption_shares(
    request: Request,
    tally_name: str,
    skip: int = 0,
    limit: int = 100,
    data: BaseQueryRequest = Body(...),
) -> DecryptionShareResponse:
    """Find descryption shares for a specific tally."""
    shares = filter_decryption_shares(
        tally_name, data.filter, skip, limit, request.app.state.settings
    )
    return DecryptionShareResponse(
        shares=shares,
    )
