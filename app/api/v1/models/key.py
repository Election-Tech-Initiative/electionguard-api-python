from typing import Any, Dict, List, Optional
from enum import Enum

from electionguard.types import GUARDIAN_ID

from .base import Base, BaseRequest, BaseResponse


__all__ = [
    "GuardianAnnounceRequest",
    "GuardianSubmitBackupRequest",
    "GuardianQueryResponse",
    "GuardianSubmitVerificationRequest",
    "GuardianSubmitChallengeRequest",
    "KeyCeremony",
    "KeyCeremonyState",
    "KeyCeremonyGuardian",
    "KeyCeremonyGuardianStatus",
    "KeyCeremonyGuardianState",
    "KeyCeremonyCreateRequest",
    "KeyCeremonyStateResponse",
    "KeyCeremonyQueryResponse",
    "KeyCeremonyVerifyChallengesResponse",
    "ElectionJointKeyResponse",
]

ElectionPublicKey = Any
ElGamalKeyPair = Any
PublicKeySet = Any

ElectionPartialKeyBackup = Any
ElectionPartialKeyVerification = Any
ElectionPartialKeyChallenge = Any

ElectionJointKey = Any


class KeyCeremonyState(str, Enum):
    """Enumeration expressing the state of the key caremony."""

    CREATED = "CREATED"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CHALLENGED = "CHALLENGED"
    CANCELLED = "CANCELLED"


class KeyCeremonyGuardianStatus(str, Enum):
    """Enumeration expressing the status of a guardian's operations."""

    INCOMPLETE = "INCOMPLETE"
    ERROR = "ERROR"
    COMPLETE = "COMPLETE"


class KeyCeremonyGuardianState(Base):
    """The Key Ceremony Guardian State describes the operations each guardian must fulfill to complete a key ceremony."""

    public_key_shared: KeyCeremonyGuardianStatus
    backups_shared: KeyCeremonyGuardianStatus
    backups_verified: KeyCeremonyGuardianStatus


class KeyCeremonyGuardian(Base):
    """Key Ceremony Guardain object is a record of the public data exchanged between guardians."""

    guardian_id: GUARDIAN_ID
    name: str
    sequence_order: int
    number_of_guardians: int
    quorum: int
    key_name: str
    public_keys: Optional[PublicKeySet]
    backups: Optional[List[ElectionPartialKeyBackup]]
    verifications: Optional[List[ElectionPartialKeyVerification]]
    challenges: Optional[List[ElectionPartialKeyChallenge]]


class KeyCeremony(Base):
    """The Key Ceremony is a record of the state of a key ceremony."""

    key_name: str
    state: KeyCeremonyState
    number_of_guardians: int
    quorum: int
    guardian_ids: List[GUARDIAN_ID]
    guardian_status: Dict[GUARDIAN_ID, KeyCeremonyGuardianState]
    election_joint_key: Optional[ElectionJointKey]


class KeyCeremonyStateResponse(Base):
    key_name: str
    state: KeyCeremonyState
    guardian_status: Dict[GUARDIAN_ID, KeyCeremonyGuardianState]


class KeyCeremonyQueryResponse(BaseResponse):
    key_ceremonies: List[KeyCeremony]


class KeyCeremonyVerifyChallengesResponse(BaseResponse):
    verifications: List[ElectionPartialKeyVerification]


class GuardianAnnounceRequest(BaseRequest):
    """A set of public auxiliary and election keys"""

    key_name: str
    """The Key Ceremony to announce"""
    public_keys: PublicKeySet


class GuardianQueryResponse(BaseResponse):
    guardians: List[KeyCeremonyGuardian]


class GuardianSubmitBackupRequest(BaseRequest):
    key_name: str
    guardian_id: str
    backups: List[ElectionPartialKeyBackup]


class GuardianSubmitVerificationRequest(BaseRequest):
    key_name: str
    guardian_id: str
    verifications: List[ElectionPartialKeyVerification]


class GuardianSubmitChallengeRequest(BaseRequest):
    key_name: str
    guardian_id: str
    challenges: List[ElectionPartialKeyChallenge]


class AuxiliaryPublicKeyRequest(BaseRequest):
    """Auxiliary public key and owner information"""

    owner_id: str
    sequence_order: int
    key: str


class KeyCeremonyCreateRequest(BaseRequest):
    """Request to create a new key ceremony"""

    key_name: str
    number_of_guardians: int
    quorum: int
    guardian_ids: List[str]


class PublishElectionJointKeyRequest(BaseRequest):
    """Request to publish the election joint key"""

    key_name: str
    election_public_keys: List[ElectionPublicKey]


class ElectionJointKeyResponse(BaseResponse):
    """Response object containing the Election Joint Key"""

    joint_key: ElectionJointKey
