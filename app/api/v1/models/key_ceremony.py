from typing import Any, Dict, List, Optional
from enum import Enum

from electionguard.type import GUARDIAN_ID

from .base import Base, BaseRequest, BaseResponse
from .key_guardian import KeyCeremonyGuardianState, ElectionPartialKeyVerification

__all__ = [
    "KeyCeremony",
    "KeyCeremonyState",
    "KeyCeremonyCreateRequest",
    "KeyCeremonyStateResponse",
    "KeyCeremonyQueryResponse",
    "KeyCeremonyVerifyChallengesResponse",
    "PublishElectionJointKeyRequest",
    "ElectionJointKeyResponse",
]

ElectionPublicKey = Any
ElGamalKeyPair = Any

ElectionJointKey = Any
ElementModQ = Any


class KeyCeremonyState(str, Enum):
    """Enumeration expressing the state of the key caremony."""

    CREATED = "CREATED"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CHALLENGED = "CHALLENGED"
    CANCELLED = "CANCELLED"


class KeyCeremony(Base):
    """The Key Ceremony is a record of the state of a key ceremony."""

    key_name: str
    state: KeyCeremonyState
    number_of_guardians: int
    quorum: int
    guardian_ids: List[GUARDIAN_ID]
    guardian_status: Dict[GUARDIAN_ID, KeyCeremonyGuardianState]
    elgamal_public_key: Optional[ElectionJointKey] = None
    commitment_hash: Optional[ElementModQ] = None


class KeyCeremonyStateResponse(Base):
    """Returns a subset of KeyCeremony data that describes only the state."""

    key_name: str
    state: KeyCeremonyState
    guardian_status: Dict[GUARDIAN_ID, KeyCeremonyGuardianState]


class KeyCeremonyQueryResponse(BaseResponse):
    """Returns a collection of Key Ceremonies."""

    key_ceremonies: List[KeyCeremony]


class KeyCeremonyVerifyChallengesResponse(BaseResponse):
    """Returns a collection of Partial Key Verifications."""

    verifications: List[ElectionPartialKeyVerification]


class KeyCeremonyCreateRequest(BaseRequest):
    """Request to create a new key ceremony."""

    key_name: str
    number_of_guardians: int
    quorum: int
    guardian_ids: List[str]


class PublishElectionJointKeyRequest(BaseRequest):
    """Request to publish the election joint key."""

    key_name: str
    election_public_keys: List[ElectionPublicKey]


class ElectionJointKeyResponse(BaseResponse):
    """Response object containing the Election Joint Key."""

    elgamal_public_key: ElectionJointKey
    commitment_hash: ElementModQ
