from typing import Any, Dict, List, Optional

from .base import Base, BaseRequest, BaseResponse, BaseValidationRequest
from .election import CiphertextElectionContext
from .manifest import ElectionManifest


__all__ = [
    "BallotQueryResponse",
    "BallotInventory",
    "BallotInventoryResponse",
    "BaseBallotRequest",
    "CastBallotsRequest",
    "SpoilBallotsRequest",
    "SubmitBallotsRequest",
    "ValidateBallotRequest",
]

DecryptionShare = Any
SubmittedBallot = Any
CiphertextBallot = Any
PlaintextBallot = Any

BALLOT_CODE = str
BALLOT_URL = str


class BallotInventory(Base):
    """
    The Ballot Inventory retains metadata about ballots in an election,
    including mappings of ballot tracking codes to ballot id's
    """

    election_id: str
    cast_ballot_count: int = 0
    spoiled_ballot_count: int = 0
    cast_ballots: Dict[BALLOT_CODE, BALLOT_URL] = {}
    """
    Collection of cast ballot codes mapped to a route that is accessible.

    Note: the BALLOT_URL is storage dependent and is not meant to be shared with the election record
    """
    spoiled_ballots: Dict[BALLOT_CODE, BALLOT_URL] = {}
    """
    Collection of spoiled ballot codes mapped to a route that is accessible.

    Note: the BALLOT_URL is storage dependent and is not meant to be shared with the election record
    """


class BallotInventoryResponse(BaseResponse):
    inventory: BallotInventory


class BallotQueryResponse(BaseResponse):
    election_id: str
    ballots: List[CiphertextBallot] = []


class BaseBallotRequest(BaseRequest):
    election_id: Optional[str] = None
    manifest: Optional[ElectionManifest] = None
    context: Optional[CiphertextElectionContext] = None


class CastBallotsRequest(BaseBallotRequest):
    """Cast the enclosed ballots."""

    ballots: List[CiphertextBallot]


class SpoilBallotsRequest(BaseBallotRequest):
    """Spoil the enclosed ballots."""

    ballots: List[CiphertextBallot]


class SubmitBallotsRequest(BaseBallotRequest):
    """Submit a ballot against a specific election."""

    ballots: List[SubmittedBallot]


class ValidateBallotRequest(BaseValidationRequest):
    """Submit a ballot against a specific election description and contest to determine if it is accepted."""

    ballot: CiphertextBallot
    manifest: ElectionManifest
    context: CiphertextElectionContext
