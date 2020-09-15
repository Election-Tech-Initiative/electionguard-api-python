from typing import Any, List, Optional

from .base import Base
from .election import ElectionDecription, CiphertextElectionContext


CiphertextAcceptedBallot = Any
CiphertextBallot = Any
PlaintextBallot = Any


class AcceptBallotRequest(Base):
    ballot: CiphertextBallot
    description: ElectionDecription
    context: CiphertextElectionContext


class EncryptBallotsRequest(Base):
    ballots: List[PlaintextBallot]
    seed_hash: str
    nonce: Optional[str] = None
    description: ElectionDecription
    context: CiphertextElectionContext


class EncryptBallotsResponse(Base):
    encrypted_ballots: List[PlaintextBallot]
    tracking_hash: str
