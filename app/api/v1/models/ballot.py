from typing import Any, List, Optional

from .base import Base
from .election import ElectionDescription, CiphertextElectionContext


__all__ = [
    "CiphertextAcceptedBallot",
    "CiphertextBallot",
    "PlaintextBallot",
    "AcceptBallotRequest",
    "EncryptBallotsRequest",
    "EncryptBallotsResponse",
]

CiphertextAcceptedBallot = Any
CiphertextBallot = Any
PlaintextBallot = Any


class AcceptBallotRequest(Base):
    ballot: CiphertextBallot
    description: ElectionDescription
    context: CiphertextElectionContext


class EncryptBallotsRequest(Base):
    ballots: List[PlaintextBallot]
    seed_hash: str
    nonce: Optional[str] = None
    description: ElectionDescription
    context: CiphertextElectionContext


class EncryptBallotsResponse(Base):
    encrypted_ballots: List[PlaintextBallot]
    next_seed_hash: str
