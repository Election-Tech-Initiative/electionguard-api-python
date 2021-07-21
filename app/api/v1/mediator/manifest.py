from typing import Any, Optional, Tuple

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status

from electionguard.group import hex_to_q
from electionguard.manifest import Manifest as sdk_manifest
from electionguard.schema import validate_json_schema
from electionguard.serializable import write_json_object
from electionguard.utils import get_optional

from app.core.schema import get_description_schema

from ....core.manifest import get_manifest, set_manifest, filter_manifests
from ..models import (
    Manifest,
    BaseQueryRequest,
    ManifestQueryResponse,
    ManifestSubmitResponse,
    ValidateManifestRequest,
    ValidateManifestResponse,
    ResponseStatus,
)
from ..tags import MANIFEST

router = APIRouter()


@router.get("", response_model=ManifestQueryResponse, tags=[MANIFEST])
def fetch_manifest(request: Request, manifest_hash: str) -> ManifestQueryResponse:
    """Get an election manifest by hash"""
    crypto_hash = hex_to_q(manifest_hash)
    if not crypto_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="manifest hash not valid"
        )
    manifest = get_manifest(crypto_hash, request.app.state.settings)
    return ManifestQueryResponse(
        manifests=[manifest],
    )


@router.put(
    "",
    response_model=ManifestSubmitResponse,
    tags=[MANIFEST],
    status_code=status.HTTP_202_ACCEPTED,
)
def submit_manifest(
    request: Request,
    data: ValidateManifestRequest = Body(...),
    schema: Any = Depends(get_description_schema),
) -> ManifestSubmitResponse:
    """
    Submit a manifest for storage
    """
    sdk_manifest, validation = _validate_manifest(data, schema)
    if not sdk_manifest or validation.status == ResponseStatus.FAIL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=validation.details
        )
    api_manifest = Manifest(
        manifest_hash=write_json_object(sdk_manifest.crypto_hash()),
        manifest=sdk_manifest.to_json_object(),
    )
    return set_manifest(api_manifest, request.app.state.settings)


@router.post("/find", response_model=ManifestQueryResponse, tags=[MANIFEST])
def find_manifests(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    data: BaseQueryRequest = Body(...),
) -> ManifestQueryResponse:
    """
    Find manifests.

    Search the repository for manifests that match the filter criteria specified in the request body.
    If no filter criteria is specified the API will iterate all available data.
    """
    filter = write_json_object(data.filter) if data.filter else {}
    return filter_manifests(filter, skip, limit, request.app.state.settings)


@router.post("/validate", response_model=ValidateManifestResponse, tags=[MANIFEST])
def validate_manifest(
    request: ValidateManifestRequest = Body(...),
    schema: Any = Depends(get_description_schema),
) -> ValidateManifestResponse:
    """
    Validate an Election manifest for a given election.
    """

    _, response = _validate_manifest(request, schema)
    return response


def _deserialize_manifest(data: object) -> Optional[sdk_manifest]:
    try:
        return sdk_manifest.from_json_object(data)
    except Exception:  # pylint: disable=broad-except
        # TODO: some sort of information why it failed
        return None


def _validate_manifest(
    request: ValidateManifestRequest, schema: Any
) -> Tuple[Optional[sdk_manifest], ValidateManifestResponse]:
    # Check schema
    schema = request.schema_override if request.schema_override else schema
    (schema_success, schema_details) = validate_json_schema(request.manifest, schema)

    # Check object parse
    manifest = _deserialize_manifest(request.manifest)
    serialize_success = bool(manifest)
    valid_success = bool(serialize_success and get_optional(manifest).is_valid())

    # build response
    success = schema_success and serialize_success and valid_success

    if success:
        return manifest, ValidateManifestResponse(
            message="Manifest successfully validated",
            manifest_hash=get_optional(manifest).crypto_hash().to_hex(),
        )

    return manifest, ValidateManifestResponse(
        status=ResponseStatus.FAIL,
        message="Manifest failed validation",
        details=str(
            {
                "schema_success": schema_success,
                "serialize_success": serialize_success,
                "valid_success": valid_success,
                "schema_details": schema_details,
            }
        ),
    )
