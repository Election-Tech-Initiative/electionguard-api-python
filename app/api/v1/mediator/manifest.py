from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, status

from electionguard.manifest import Manifest
from electionguard.schema import validate_json_schema

from app.core.schema import get_description_schema

from ..models import ValidateManifestRequest, BaseValidationResponse, ResponseStatus
from ..tags import MANIFEST

router = APIRouter()


@router.post("/validate", tags=[MANIFEST], status_code=status.HTTP_204_NO_CONTENT)
def validate_election_manifest(
    request: ValidateManifestRequest = Body(...),
    schema: Any = Depends(get_description_schema),
) -> BaseValidationResponse:
    """
    Validate an Election manifest for a given election.
    """

    success = ResponseStatus.SUCCESS
    message = "Election manifest successfully validated"
    details = None

    # Check schema
    schema = request.schema_override if request.schema_override else schema
    (schema_success, error_details) = validate_json_schema(request.manifest, schema)
    if not schema_success:
        success = ResponseStatus.SUCCESS if schema_success else ResponseStatus.FAIL
        message = "Election description did not match schema"
        details = error_details

    # Check object parse
    manifest: Optional[Manifest] = None
    if success:
        try:
            manifest = Manifest.from_json_object(request.manifest)
        except Exception:  # pylint: disable=broad-except
            success = ResponseStatus.FAIL
            message = "Election description could not be read from JSON"

    if success:
        if manifest:
            valid_success = manifest.is_valid()
            if not valid_success:
                message = "Election description was not valid well formed data"

    # Check
    return BaseValidationResponse(status=success, message=message, details=details)
