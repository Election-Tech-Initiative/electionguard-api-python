from typing import Optional

from electionguard.ballot import PlaintextBallot
from electionguard.election import CiphertextElectionContext
from electionguard.manifest import InternalManifest, Manifest
from electionguard.encrypt import encrypt_ballot
from electionguard.group import ElementModQ
from electionguard.serializable import read_json_object, write_json_object
from electionguard.utils import get_optional
from fastapi import APIRouter, Body, HTTPException

from ..models import (
    ResponseStatus,
    EncryptBallotsRequest,
    EncryptBallotsResponse,
)
from ..tags import ENCRYPT

router = APIRouter()


@router.post("/encrypt", tags=[ENCRYPT])
def encrypt_ballots(
    request: EncryptBallotsRequest = Body(...),
) -> EncryptBallotsResponse:
    """
    Encrypt one or more ballots
    """
    ballots = [PlaintextBallot.from_json_object(ballot) for ballot in request.ballots]
    description = InternalManifest(Manifest.from_json_object(request.manifest))
    context = CiphertextElectionContext.from_json_object(request.context)
    seed_hash = read_json_object(request.seed_hash, ElementModQ)
    nonce: Optional[ElementModQ] = (
        read_json_object(request.nonce, ElementModQ) if request.nonce else None
    )

    encrypted_ballots = []
    current_hash = seed_hash

    for ballot in ballots:
        encrypted_ballot = encrypt_ballot(
            ballot, description, context, current_hash, nonce
        )
        if not encrypted_ballot:
            raise HTTPException(status_code=500, detail="Ballot failed to encrypt")
        encrypted_ballots.append(encrypted_ballot)
        current_hash = get_optional(encrypted_ballot.crypto_hash)

    response = EncryptBallotsResponse(
        status=ResponseStatus.SUCCESS,
        message="Successfully encrypted ballots",
        encrypted_ballots=[ballot.to_json_object() for ballot in encrypted_ballots],
        next_seed_hash=write_json_object(current_hash),
    )
    return response
