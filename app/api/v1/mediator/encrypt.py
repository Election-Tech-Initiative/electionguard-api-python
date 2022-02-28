from fastapi import APIRouter, Body, HTTPException, Request, status

from electionguard.ballot import PlaintextBallot
from electionguard.election import CiphertextElectionContext
from electionguard.manifest import InternalManifest, Manifest
from electionguard.encrypt import encrypt_ballot
from electionguard.group import ElementModQ
from electionguard.serializable import read_json_object, write_json_object
from electionguard.utils import get_optional

from app.core.election import get_election
from ..models import (
    EncryptBallotsRequest,
    EncryptBallotsResponse,
)
from ..tags import ENCRYPT

router = APIRouter()


@router.post("/encrypt", tags=[ENCRYPT])
def encrypt_ballots(
    request: Request,
    data: EncryptBallotsRequest = Body(...),
) -> EncryptBallotsResponse:
    """
    Encrypt one or more ballots.

    This function is primarily used for testing and does not modify internal state.
    """
    election = get_election(data.election_id, request.app.state.settings)
    manifest = InternalManifest(Manifest.from_json_object(election.manifest))
    context = election.context.to_sdk_format()
    seed_hash = read_json_object(data.seed_hash, ElementModQ)

    ballots = [PlaintextBallot.from_json_object(ballot) for ballot in data.ballots]

    encrypted_ballots = []
    current_hash = seed_hash

    for ballot in ballots:
        encrypted_ballot = encrypt_ballot(ballot, manifest, context, current_hash)
        if not encrypted_ballot:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ballot failed to encrypt",
            )
        encrypted_ballots.append(encrypted_ballot)
        current_hash = get_optional(encrypted_ballot.crypto_hash)

    response = EncryptBallotsResponse(
        message="Successfully encrypted ballots",
        encrypted_ballots=[ballot.to_json_object() for ballot in encrypted_ballots],
        next_seed_hash=write_json_object(current_hash),
    )
    return response
