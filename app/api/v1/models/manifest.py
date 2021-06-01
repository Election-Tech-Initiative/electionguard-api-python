from typing import Any, Optional

from .base import BaseRequest, BaseResponse, BaseValidationRequest

__all__ = ["ManifestSubmitResponse", "ManifestQueryResponse", "ValidateManifestRequest"]

ElectionManifest = Any
ElementModQ = Any


class ManifestSubmitResponse(BaseResponse):
    manifest_hash: ElementModQ


class ManifestQueryResponse(BaseResponse):
    manifest: ElectionManifest


class ValidateManifestRequest(BaseValidationRequest):
    """
    A request to validate an Election Description
    """

    manifest: ElectionManifest
    """The manifest to validate"""
