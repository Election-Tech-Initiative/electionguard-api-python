from electionguard.ballot import CiphertextAcceptedBallot
from electionguard.decrypt_with_shares import decrypt_tally as decrypt
from electionguard.decryption import compute_decryption_share
from electionguard.decryption_share import TallyDecryptionShare
from electionguard.election import (
    CiphertextElectionContext,
    ElectionDescription,
    InternalElectionDescription,
)
from electionguard.serializable import write_json_object
from electionguard.tally import (
    publish_ciphertext_tally,
    publish_plaintext_tally,
    CiphertextTally,
    PublishedCiphertextTally,
)
from fastapi import APIRouter, Body, HTTPException
from typing import Any, List, Tuple

from app.utils.serialize import read_json_object
from ..models import (
    convert_guardian,
    convert_tally,
    AppendTallyRequest,
    DecryptTallyRequest,
    DecryptTallyShareRequest,
    StartTallyRequest,
)
from ..tags import GUARDIAN_ONLY

router = APIRouter()


@router.post("")
def start_tally(request: StartTallyRequest = Body(...)) -> Any:
    """
    Start a new tally of a collection of ballots
    """

    ballots, description, context = _parse_tally_request(request)
    tally = CiphertextTally("election-results", description, context)

    return _tally_ballots(tally, ballots)


@router.post("/append")
def append_to_tally(request: AppendTallyRequest = Body(...)) -> Any:
    """
    Append ballots into an existing tally
    """

    ballots, description, context = _parse_tally_request(request)
    tally = convert_tally(request.encrypted_tally, description, context)

    return _tally_ballots(tally, ballots)


@router.post("/decrypt")
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
    published_plaintext_tally = publish_plaintext_tally(full_plaintext_tally)

    return published_plaintext_tally.to_json_object()


@router.post("/decrypt-share", tags=[GUARDIAN_ONLY])
def decrypt_share(request: DecryptTallyShareRequest = Body(...)) -> Any:
    """
    Decrypt a single guardian's share of a tally
    """
    description = InternalElectionDescription(
        ElectionDescription.from_json_object(request.description)
    )
    context = CiphertextElectionContext.from_json_object(request.context)
    guardian = convert_guardian(request.guardian)
    tally = convert_tally(request.encrypted_tally, description, context)

    share = compute_decryption_share(guardian, tally, context)

    return write_json_object(share)


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
    tally: CiphertextTally, ballots: List[CiphertextAcceptedBallot]
) -> PublishedCiphertextTally:
    """
    Append a series of ballots to a new or existing tally
    """
    tally_succeeded = tally.batch_append(ballots)

    if tally_succeeded:
        published_tally = publish_ciphertext_tally(tally)
        return published_tally.to_json_object()
    else:
        raise HTTPException(status_code=500, detail="Unable to tally ballots")
