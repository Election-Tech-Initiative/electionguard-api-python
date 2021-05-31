from typing import Any
from electionguard.election import (
    ElectionConstants,
    make_ciphertext_election_context,
)
from electionguard.group import ElementModP, ElementModQ
from electionguard.manifest import Manifest
from electionguard.serializable import read_json_object, write_json_object

from fastapi import APIRouter, Body

from ..models import (
    MakeElectionContextRequest,
)
from ..tags import ELECTION

router = APIRouter()


@router.get("/constants", tags=[ELECTION])
def get_election_constants() -> Any:
    """
    Return the constants defined for an election
    """
    constants = ElectionConstants()
    return constants.to_json_object()


@router.post("/context", tags=[ELECTION])
def build_election_context(request: MakeElectionContextRequest = Body(...)) -> Any:
    """
    Build a CiphertextElectionContext for a given election
    """
    manifest: Manifest = Manifest.from_json_object(request.manifest)
    elgamal_public_key: ElementModP = read_json_object(
        request.elgamal_public_key, ElementModP
    )
    commitment_hash = read_json_object(request.commitment_hash, ElementModQ)
    number_of_guardians = request.number_of_guardians
    quorum = request.quorum

    context = make_ciphertext_election_context(
        number_of_guardians,
        quorum,
        elgamal_public_key,
        commitment_hash,
        manifest.crypto_hash(),
    )

    return write_json_object(context)
