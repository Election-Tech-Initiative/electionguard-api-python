from typing import Any, List, Optional
from enum import Enum
from datetime import datetime

from .base import BaseResponse, BaseRequest, Base

__all__ = [
    "CiphertextTally",
    "CiphertextTallyQueryResponse",
    "DecryptTallyRequest",
    "PlaintextTally",
    "PlaintextTallyState",
    "PlaintextTallyQueryResponse",
]

ElectionGuardCiphertextTally = Any
ElectionGuardPlaintextTally = Any


class CiphertextTally(Base):
    """A Tally for a specific election."""

    election_id: str
    tally_name: str
    created: datetime
    tally: ElectionGuardCiphertextTally
    """The full electionguard CiphertextTally that includes the cast and spoiled ballot id's."""


class PlaintextTallyState(str, Enum):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    ERROR = "ERROR"
    COMPLETE = "COMPLETE"


class PlaintextTally(Base):
    """A plaintext tally for a specific election."""

    election_id: str
    tally_name: str
    created: datetime
    state: PlaintextTallyState
    tally: Optional[ElectionGuardPlaintextTally] = None


class CiphertextTallyQueryResponse(BaseResponse):
    """A collection of Ciphertext Tallies."""

    tallies: List[CiphertextTally] = []


class PlaintextTallyQueryResponse(BaseResponse):
    """A collection of Plaintext Tallies."""

    tallies: List[PlaintextTally] = []


class DecryptTallyRequest(BaseRequest):
    """A request to decrypt a specific tally.  Can optionally include the tally to decrypt."""

    election_id: str
    tally_name: str
