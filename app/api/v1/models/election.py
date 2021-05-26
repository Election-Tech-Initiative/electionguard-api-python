from typing import Any

from .base import Base
from .validation import BaseValidationRequest


__all__ = [
    "CiphertextElectionContext",
    "ElectionContextRequest",
    "ElectionDescription",
    "ValidateElectionDescriptionRequest",
]

ElectionDescription = Any

CiphertextElectionContext = Any


class ElectionContextRequest(Base):
    """
    A request to build an Election Context for a given election
    """

    description: ElectionDescription
    elgamal_public_key: str
    # commitment_hash: str
    number_of_guardians: int
    quorum: int


class ValidateElectionDescriptionRequest(BaseValidationRequest):
    """
    A request to validate an Election Description
    """

    description: ElectionDescription
