from typing import Any

from .base import BaseValidationRequest

__all__ = ["ValidateManifestRequest"]

ElectionManifest = Any


class ValidateManifestRequest(BaseValidationRequest):
    """
    A request to validate an Election Description
    """

    manifest: ElectionManifest
    """The manifest to validate"""
