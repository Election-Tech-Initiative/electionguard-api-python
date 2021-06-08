from typing import Any, List, Optional

from .base import (
    BaseRequest,
    BaseResponse,
    BaseValidationRequest,
    BaseValidationResponse,
)

__all__ = [
    "ManifestSubmitResponse",
    "ManifestQueryRequest",
    "ManifestQueryResponse",
    "ValidateManifestRequest",
    "ValidateManifestResponse",
]

ElectionManifest = Any
ElementModQ = Any


class ManifestSubmitResponse(BaseResponse):
    manifest_hash: ElementModQ


class ManifestQueryRequest(BaseRequest):
    """A request for manifests using the specified filter"""

    filter: Optional[Any] = None


class ManifestQueryResponse(BaseResponse):
    manifests: List[ElectionManifest]


class ValidateManifestRequest(BaseValidationRequest):
    """
    A request to validate an Election Description
    """

    manifest: ElectionManifest
    """The manifest to validate"""


class ValidateManifestResponse(BaseValidationResponse):
    manifest_hash: Optional[str] = None
