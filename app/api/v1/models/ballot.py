from typing import Any, Dict, List, Optional

from .base import Base
from .election import ElectionDescription, CiphertextElectionContext
from .guardian import Guardian, GuardianId


__all__ = [
    "AcceptBallotRequest",
    "SubmittedBallot",
    "CiphertextBallot",
    "DecryptBallotSharesRequest",
    "DecryptBallotSharesResponse",
    "DecryptBallotsRequest",
    "EncryptBallotsRequest",
    "EncryptBallotsResponse",
    "PlaintextBallot",
]

DecryptionShare = Any
SubmittedBallot = Any
CiphertextBallot = Any
PlaintextBallot = Any


class AcceptBallotRequest(Base):
    ballot: CiphertextBallot
    description: ElectionDescription
    context: CiphertextElectionContext


class DecryptBallotsRequest(Base):
    encrypted_ballots: List[SubmittedBallot]
    shares: Dict[GuardianId, List[DecryptionShare]]
    context: CiphertextElectionContext


class DecryptBallotSharesRequest(Base):
    encrypted_ballots: List[SubmittedBallot]
    guardian: Guardian
    context: CiphertextElectionContext


class DecryptBallotSharesResponse(Base):
    shares: List[DecryptionShare]


class EncryptBallotsRequest(Base):
    ballots: List[PlaintextBallot]
    seed_hash: str
    nonce: Optional[str] = None
    description: ElectionDescription
    context: CiphertextElectionContext


class EncryptBallotsResponse(Base):
    encrypted_ballots: List[PlaintextBallot]
    next_seed_hash: str
