from typing import Any, Dict, List, Optional

from .base import Base
from .election import ElectionDescription, CiphertextElectionContext
from .guardian import Guardian, GuardianId


__all__ = [
    "AcceptBallotRequest",
    "CiphertextAcceptedBallot",
    "CiphertextBallot",
    "DecryptBallotSharesRequest",
    "DecryptBallotSharesResponse",
    "DecryptBallotsRequest",
    "EncryptBallotsRequest",
    "EncryptBallotsResponse",
    "PlaintextBallot",
]

BallotDecryptionShare = Any
CiphertextAcceptedBallot = Any
CiphertextBallot = Any
PlaintextBallot = Any


class AcceptBallotRequest(Base):
    ballot: CiphertextBallot
    description: ElectionDescription
    context: CiphertextElectionContext


class DecryptBallotsRequest(Base):
    encrypted_ballots: List[CiphertextAcceptedBallot]
    shares: Dict[GuardianId, List[BallotDecryptionShare]]
    context: CiphertextElectionContext


class DecryptBallotSharesRequest(Base):
    encrypted_ballots: List[CiphertextAcceptedBallot]
    guardian: Guardian
    context: CiphertextElectionContext


class DecryptBallotSharesResponse(Base):
    shares: List[BallotDecryptionShare]


class EncryptBallotsRequest(Base):
    ballots: List[PlaintextBallot]
    seed_hash: str
    nonce: Optional[str] = None
    description: ElectionDescription
    context: CiphertextElectionContext


class EncryptBallotsResponse(Base):
    encrypted_ballots: List[PlaintextBallot]
    next_seed_hash: str
