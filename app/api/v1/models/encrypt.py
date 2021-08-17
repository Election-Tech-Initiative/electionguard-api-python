from typing import Any, List

from .base import BaseRequest, BaseResponse


__all__ = [
    "EncryptBallotsRequest",
    "EncryptBallotsResponse",
]

CiphertextBallot = Any
PlaintextBallot = Any


class EncryptBallotsRequest(BaseRequest):
    """A request to encrypt the enclosed ballots."""

    election_id: str
    seed_hash: str
    ballots: List[PlaintextBallot]


class EncryptBallotsResponse(BaseResponse):
    encrypted_ballots: List[CiphertextBallot]
    """The encrypted representations of the plaintext ballots."""
    next_seed_hash: str
    """A seed hash which can optionally be used for the next call to encrypt."""
