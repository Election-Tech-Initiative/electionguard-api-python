from typing import Any, List, Optional

from .base import (
    Base,
    BaseRequest,
    BaseResponse,
    BaseValidationRequest,
    BaseValidationResponse,
)

__all__ = [
    "Manifest",
    "ManifestSubmitResponse",
    "ManifestQueryResponse",
    "ValidateManifestRequest",
    "ValidateManifestResponse",
]

ElectionManifest = Any
ElementModQ = Any


class Manifest(Base):
    manifest_hash: ElementModQ
    manifest: ElectionManifest


class ManifestSubmitResponse(BaseResponse):
    manifest_hash: ElementModQ


class ManifestQueryResponse(BaseResponse):
    manifests: List[Manifest]


class ValidateManifestRequest(BaseValidationRequest):
    """
    A request to validate an Election Description
    """

    manifest: ElectionManifest
    """The manifest to validate"""


class ValidateManifestResponse(BaseValidationResponse):
    manifest_hash: Optional[str] = None
