# pylint: disable=unused-argument
from datetime import datetime
from typing import Dict
from electionguard.election import CiphertextElectionContext
from electionguard.scheduler import Scheduler
from electionguard.manifest import ElectionType, Manifest, InternalManifest
from electionguard.tally import CiphertextTally, CiphertextTallyContest
from electionguard.serializable import read_json_object, write_json_object
from electionguard.types import CONTEST_ID
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status

from app.core.scheduler import get_scheduler
from app.core.guardian import get_guardian
from app.core.tally_decrypt import get_decryption_share, set_decryption_share
from ..models import (
    to_sdk_guardian,
    DecryptTallyShareRequest,
    CiphertextTallyDecryptionShare,
    DecryptionShareResponse,
)
from ..tags import TALLY_DECRYPT

router = APIRouter()


@router.get(
    "/decrypt-share", response_model=DecryptionShareResponse, tags=[TALLY_DECRYPT]
)
def fetch_decrypt_share(
    request: Request,
    election_id: str,
    tally_name: str,
) -> DecryptionShareResponse:
    """
    Fetch A decryption share for a given tally
    """
    share = get_decryption_share(election_id, tally_name, request.app.state.settings)
    return DecryptionShareResponse(shares=[share])


@router.post(
    "/decrypt-share", response_model=DecryptionShareResponse, tags=[TALLY_DECRYPT]
)
def decrypt_share(
    request: Request,
    data: DecryptTallyShareRequest = Body(...),
    scheduler: Scheduler = Depends(get_scheduler),
) -> DecryptionShareResponse:
    """
    Decrypt a single guardian's share of a tally
    """
    guardian = get_guardian(data.guardian_id, request.app.state.settings)
    context = CiphertextElectionContext.from_json_object(data.context)

    # TODO: HACK: Remove The Empty Manifest
    # Note: The CiphertextTally requires an internal manifest passed into its constructor
    # but it is not actually used when executing `compute_decryption_share` so we create a fake.
    # see: https://github.com/microsoft/electionguard-python/issues/391
    internal_manifest = InternalManifest(
        Manifest(
            "",
            "",
            ElectionType.other,
            datetime.now(),
            datetime.now(),
            [],
            [],
            [],
            [],
            [],
        )
    )
    tally = CiphertextTally(data.encrypted_tally.tally_name, internal_manifest, context)
    contests: Dict[CONTEST_ID, CiphertextTallyContest] = {
        contest_id: read_json_object(contest, CiphertextTallyContest)
        for contest_id, contest in data.encrypted_tally.tally["contests"].items()
    }
    tally.contests = contests

    # TODO: modify compute_tally_share to include an optional scheduler param
    sdk_guardian = to_sdk_guardian(guardian)
    sdk_tally_share = sdk_guardian.compute_tally_share(tally, context)

    if not sdk_tally_share:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not compute tally share",
        )

    share = CiphertextTallyDecryptionShare(
        election_id=data.encrypted_tally.election_id,
        tally_name=data.encrypted_tally.tally_name,
        guardian_id=guardian.guardian_id,
        tally_share=write_json_object(sdk_tally_share),
        # TODO: include spoiled ballots
    )

    set_decryption_share(share, request.app.state.settings)

    return DecryptionShareResponse(shares=[share])
