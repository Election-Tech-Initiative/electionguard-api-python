from os.path import realpath, join
from typing import Any
from electionguard.election import (
    ElectionDescription,
    ElectionConstants,
    make_ciphertext_election_context,
)
from electionguard.group import ElementModP
from electionguard.serializable import read_json_object, write_json_object
from fastapi import APIRouter, Body

from ..models import ElectionContextRequest
from ..tags import CONFIGURE_ELECTION

router = APIRouter()

DATA_FOLDER_PATH = realpath(join(__file__, "../../../../data"))
DESCRIPTION_FILE = join(DATA_FOLDER_PATH, "election_description.json")
READ = "r"


@router.get("/constants", tags=[CONFIGURE_ELECTION])
def get_election_constants() -> Any:
    """
    Return the constants defined for an election
    """
    constants = ElectionConstants()
    return constants.to_json_object()


@router.post("/context", tags=[CONFIGURE_ELECTION])
def build_election_context(request: ElectionContextRequest = Body(...)) -> Any:
    """
    Build a CiphertextElectionContext for a given election
    """
    description: ElectionDescription = ElectionDescription.from_json_object(
        request.description
    )
    elgamal_public_key: ElementModP = read_json_object(
        request.elgamal_public_key, ElementModP
    )
    number_of_guardians = request.number_of_guardians
    quorum = request.quorum

    context = make_ciphertext_election_context(
        number_of_guardians, quorum, elgamal_public_key, description.crypto_hash()
    )

    return write_json_object(context)
