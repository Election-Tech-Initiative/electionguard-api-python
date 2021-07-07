from typing import Any, List, Optional
from enum import Enum

from .base import Base, BaseRequest, BaseResponse
from .manifest import ElectionManifest


__all__ = [
    "Election",
    "ElectionState",
    "ElectionQueryRequest",
    "ElectionQueryResponse",
    "MakeElectionContextRequest",
    "MakeElectionContextResponse",
    "SubmitElectionRequest",
]

CiphertextElectionContext = Any


class ElectionState(str, Enum):
    CREATED = "CREATED"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PUBLISHED = "PUBLISHED"


class Election(Base):
    """An election object"""

    election_id: str
    state: ElectionState
    context: CiphertextElectionContext
    manifest: ElectionManifest


class ElectionQueryRequest(BaseRequest):
    """A request for elections using the specified filter"""

    filter: Optional[Any] = None
    """
    a json object filter that will be applied to the search
    """

    class Config:
        schema_extra = {"example": {"filter": {"election_id": "some-election-id-123"}}}


class ElectionQueryResponse(BaseResponse):
    """A collection of elections"""

    elections: List[Election]


class SubmitElectionRequest(BaseRequest):
    """Submit an election"""

    election_id: Optional[str] = None
    context: CiphertextElectionContext
    manifest: Optional[ElectionManifest] = None


class MakeElectionContextRequest(BaseRequest):
    """
    A request to build an Election Context for a given election
    """

    elgamal_public_key: str
    commitment_hash: str
    number_of_guardians: int
    quorum: int
    manifest_hash: Optional[str] = None
    manifest: Optional[ElectionManifest] = None


class MakeElectionContextResponse(BaseResponse):
    """A Ciphertext Election Context"""

    context: CiphertextElectionContext
