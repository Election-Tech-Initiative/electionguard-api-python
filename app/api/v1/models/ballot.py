from typing import Any, List, Optional

from .base import BaseRequest, BaseResponse, BaseValidationRequest
from .election import CiphertextElectionContext
from .manifest import ElectionManifest


__all__ = [
    "BallotQueryResponse",
    "BaseBallotRequest",
    "CastBallotsRequest",
    "SpoilBallotsRequest",
    "SubmitBallotsRequest",
    "SubmitBallotsResponse",
    "ValidateBallotRequest",
]

DecryptionShare = Any
SubmittedBallot = Any
CiphertextBallot = Any
PlaintextBallot = Any


class BallotQueryResponse(BaseResponse):
    election_id: str
    ballot: Optional[CiphertextBallot] = None


class BaseBallotRequest(BaseRequest):
    election_id: Optional[str] = None
    manifest: Optional[ElectionManifest] = None
    context: Optional[CiphertextElectionContext] = None


class CastBallotsRequest(BaseBallotRequest):
    ballots: List[CiphertextBallot]


class SpoilBallotsRequest(BaseBallotRequest):
    ballots: List[CiphertextBallot]


class SubmitBallotsRequest(BaseBallotRequest):
    """Submit a ballot against a specific election"""

    ballots: List[SubmittedBallot]


class SubmitBallotsResponse(BaseResponse):
    """Submit a ballot against a specific election"""

    cache_keys: List[str]
    election_id: Optional[str] = None


class ValidateBallotRequest(BaseValidationRequest):
    """Submit a ballot against a specific election description and contest to determine if it is accepted"""

    ballot: CiphertextBallot
    manifest: ElectionManifest
    context: CiphertextElectionContext
