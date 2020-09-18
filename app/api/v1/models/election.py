from typing import Any
from .base import Base

__all__ = ["CiphertextElectionContext", "ElectionContextRequest", "ElectionDescription"]

ElectionDescription = Any

CiphertextElectionContext = Any


class ElectionContextRequest(Base):
    """
    A request to build an Election Context for a given election
    """

    description: ElectionDescription
    elgamal_public_key: str
    number_of_guardians: int
    quorum: int
