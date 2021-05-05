from os.path import realpath, join
from typing import Any, Optional
from electionguard.election import (
    ElectionConstants,
    make_ciphertext_election_context,
)
from electionguard.group import ElementModP
from electionguard.manifest import Manifest
from electionguard.schema import validate_json_schema
from electionguard.serializable import read_json_object, write_json_object

from fastapi import APIRouter, Body, Depends

from app.core.schema import get_description_schema
from ..models import (
    ElectionContextRequest,
    ValidationResponse,
    ValidateElectionDescriptionRequest,
)
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
    description: Manifest = Manifest.from_json_object(request.description)
    elgamal_public_key: ElementModP = read_json_object(
        request.elgamal_public_key, ElementModP
    )
    number_of_guardians = request.number_of_guardians
    quorum = request.quorum

    context = make_ciphertext_election_context(
        number_of_guardians,
        quorum,
        elgamal_public_key,
        description.crypto_hash(),  # need commitment hash
        description.crypto_hash(),
    )

    return write_json_object(context)


@router.post("/validate/description", tags=[CONFIGURE_ELECTION])
def validate_election_description(
    request: ValidateElectionDescriptionRequest = Body(...),
    schema: Any = Depends(get_description_schema),
) -> Any:
    """
    Validate an Election description or manifest for a given election
    """

    success = True
    message = "Election description successfully validated"
    details = ""

    # Check schema
    schema = request.schema_override if request.schema_override else schema
    (schema_success, error_details) = validate_json_schema(request.description, schema)
    if not schema_success:
        success = schema_success
        message = "Election description did not match schema"
        details = error_details

    # Check object parse
    description: Optional[Manifest] = None
    if success:
        try:
            description = Manifest.from_json_object(request.description)
        except Exception:  # pylint: disable=broad-except
            success = False
            message = "Election description could not be read from JSON"

    if success:
        if description:
            valid_success = description.is_valid()
            if not valid_success:
                message = "Election description was not valid well formed data"

    # Check
    return ValidationResponse(success=success, message=message, details=details)
