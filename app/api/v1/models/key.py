from typing import Any, Dict, List, Optional
from enum import Enum


from .base import Base, BaseRequest, BaseResponse

from electionguard.types import GUARDIAN_ID

__all__ = [
    "ElectionKeyPairRequest",
    "GuardianAnnounceRequest",
    "GuardianSubmitBackupRequest",
    "GuardianQueryResponse",
    "GuardianBackupQueryResponse",
    "GuardianSubmitVerificationRequest",
    "GuardianVerificationQueryResponse",
    "GuardianSubmitChallengeRequest",
    "GuardianChallengeQueryResponse",
    "KeyCeremony",
    "KeyCeremonyGuardian",
    "KeyCeremonyGuardianState",
    "KeyCeremonyCreateRequest",
    "KeyCeremonyStateResponse",
    "KeyCeremonyQueryResponse",
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
    CREATED = "CREATED"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CHALLENGED = "CHALLENGED"
    CANCELLED = "CANCELLED"


class KeyCeremonyGuardianStatus(str, Enum):
    INCOMPLETE = "INCOMPLETE"
    ERROR = "ERROR"
    COMPLETE = "COMPLETE"


class KeyCeremonyGuardianState(Base):
    public_key_shared: KeyCeremonyGuardianStatus
    backups_shared: KeyCeremonyGuardianStatus
    backups_verified: KeyCeremonyGuardianStatus


class KeyCeremonyGuardian(Base):
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


class GuardianBackupQueryResponse(BaseResponse):
    key_name: str
    guardian_count: int
    backups: Dict[GUARDIAN_ID, ElectionPartialKeyBackup]


class GuardianSubmitVerificationRequest(BaseRequest):
    key_name: str
    guardian_id: str
    verifications: List[ElectionPartialKeyVerification]


class GuardianVerificationQueryResponse(BaseResponse):
    key_name: str
    guardian_count: int
    backups: Dict[GUARDIAN_ID, ElectionPartialKeyVerification]


class GuardianSubmitChallengeRequest(BaseRequest):
    key_name: str
    guardian_id: str
    challenges: List[ElectionPartialKeyChallenge]


class GuardianChallengeQueryResponse(BaseResponse):
    key_name: str
    guardian_count: int
    challenges: Dict[GUARDIAN_ID, ElectionPartialKeyChallenge]


class AuxiliaryPublicKeyRequest(BaseRequest):
    """Auxiliary public key and owner information"""

    owner_id: str
    sequence_order: int
    key: str


class ElectionKeyPairRequest(BaseRequest):

    owner_id: str
    sequence_order: int
    quorum: int
    nonce: Optional[str] = None


class KeyCeremonyCreateRequest(BaseRequest):
    """Create a Key ceremony"""

    key_name: str
    number_of_guardians: int
    quorum: int
    guardian_ids: List[str]


class PublishElectionJointKeyRequest(BaseRequest):
    key_name: str
    election_public_keys: List[ElectionPublicKey]


class ElectionJointKeyResponse(BaseResponse):
    joint_key: ElectionJointKey


# TODO: deprecated
class ElectionJointKey(BaseRequest):
    joint_key: str


# TODO: deprecated
class AuxiliaryRequest(BaseRequest):
    owner_id: str
    sequence_order: int
