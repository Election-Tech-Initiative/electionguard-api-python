from typing import Any, List, Optional

from .base import BaseRequest, BaseResponse
from .election import CiphertextElectionContext
from .manifest import ElectionManifest


__all__ = [
    "EncryptBallotsRequest",
    "EncryptBallotsResponse",
]

CiphertextBallot = Any
PlaintextBallot = Any

# TODO: follow model submit ballot request object model


class EncryptBallotsRequest(BaseRequest):
    ballots: List[PlaintextBallot]
    seed_hash: str
    nonce: Optional[str] = None
    manifest: Optional[ElectionManifest] = None
    context: Optional[CiphertextElectionContext] = None


class EncryptBallotsResponse(BaseResponse):
    encrypted_ballots: List[CiphertextBallot]
    """The encrypted representations of the plaintext ballots"""
    next_seed_hash: str
    """A seed hash which can optionally be used for the next call to encrypt"""
