from typing import Any
from electionguard.decryption import compute_decryption_share
from electionguard.election import (
    CiphertextElectionContext,
    ElectionDescription,
    InternalElectionDescription,
)
from electionguard.scheduler import Scheduler
from electionguard.serializable import write_json_object
from fastapi import APIRouter, Body, Depends

from app.core.scheduler import get_scheduler
from ..models import (
    convert_guardian,
    convert_tally,
    DecryptTallyShareRequest,
)
from ..tags import TALLY

router = APIRouter()


@router.post("/decrypt-share", tags=[TALLY])
def decrypt_share(
    request: DecryptTallyShareRequest = Body(...),
    scheduler: Scheduler = Depends(get_scheduler),
) -> Any:
    """
    Decrypt a single guardian's share of a tally
    """
    description = InternalElectionDescription(
        ElectionDescription.from_json_object(request.description)
    )
    context = CiphertextElectionContext.from_json_object(request.context)
    guardian = convert_guardian(request.guardian)
    tally = convert_tally(request.encrypted_tally, description, context)

    share = compute_decryption_share(guardian, tally, context, scheduler)

    return write_json_object(share)
