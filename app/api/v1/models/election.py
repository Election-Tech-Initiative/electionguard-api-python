from typing import Any

from .base import BaseRequest
from .manifest import ElectionManifest


__all__ = [
    "MakeElectionContextRequest",
]

CiphertextElectionContext = Any


class MakeElectionContextRequest(BaseRequest):
    """
    A request to build an Election Context for a given election
    """

    manifest: ElectionManifest
    elgamal_public_key: str
    commitment_hash: str
    number_of_guardians: int
    quorum: int
