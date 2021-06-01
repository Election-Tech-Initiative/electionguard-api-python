from typing import Any, Optional, Tuple
import sys
from fastapi import APIRouter, Body, Depends, HTTPException, status, Response

from electionguard.group import ElementModQ, hex_to_q
from electionguard.manifest import Manifest
from electionguard.schema import validate_json_schema
from electionguard.utils import get_optional

from app.core.schema import get_description_schema

from ....core.repository import get_repository, DataCollection
from ..models import (
    ManifestQueryResponse,
    ManifestSubmitResponse,
    ValidateManifestRequest,
    BaseValidationResponse,
    ResponseStatus,
)
from ..tags import MANIFEST

router = APIRouter()

# TODO: multi-tenancy
CLIENT_ID = "electionguard-default-client-id"


@router.get("", tags=[MANIFEST])
def get_manifest(manifest_hash: str) -> ManifestQueryResponse:
    """Get an election manifest by hash"""
    crypto_hash = hex_to_q(manifest_hash)
    if not crypto_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="manifest hash not valid"
        )
    try:
        with get_repository(CLIENT_ID, DataCollection.MANIFEST) as repository:
            query_result = repository.get({"manifest_hash": crypto_hash.to_hex()})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find manifest {manifest_hash}",
                )

            return ManifestQueryResponse(
                status=ResponseStatus.SUCCESS,
                manifest=query_result["manifest"],
            )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="get manifest failed",
        ) from error


@router.put("", tags=[MANIFEST], status_code=status.HTTP_202_ACCEPTED)
def submit_manifest(
    request: ValidateManifestRequest = Body(...),
    schema: Any = Depends(get_description_schema),
) -> ManifestSubmitResponse:
    """
    Submit a manifest for storage
    """
    manifest, validation = _validate_manifest(request, schema)
    if not manifest or validation.status == ResponseStatus.FAIL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=validation.details
        )

    try:
        with get_repository(CLIENT_ID, DataCollection.MANIFEST) as repository:
            manifest_hash = manifest.crypto_hash().to_hex()
            print(manifest.to_json_object())
            keys = repository.set(
                {"manifest_hash": manifest_hash, "manifest": manifest.to_json_object()}
            )
            print(keys)
            return ManifestSubmitResponse(
                status=ResponseStatus.SUCCESS, manifest_hash=manifest_hash
            )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Submit manifest failed",
        ) from error


@router.post("/validate", tags=[MANIFEST], status_code=status.HTTP_204_NO_CONTENT)
def validate_manifest(
    request: ValidateManifestRequest = Body(...),
    schema: Any = Depends(get_description_schema),
) -> BaseValidationResponse:
    """
    Validate an Election manifest for a given election.
    """

    _, response = _validate_manifest(request, schema)
    return response


def _deserialize_manifest(data: object) -> Optional[Manifest]:
    try:
        return Manifest.from_json_object(data)
    except Exception:  # pylint: disable=broad-except
        # TODO: some sort of information why it failed
        return None


def _validate_manifest(
    request: ValidateManifestRequest, schema: Any
) -> Tuple[Optional[Manifest], BaseValidationResponse]:
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
        return manifest, BaseValidationResponse(
            status=ResponseStatus.SUCCESS, message="Manifest successfully validated"
        )

    return manifest, BaseValidationResponse(
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
