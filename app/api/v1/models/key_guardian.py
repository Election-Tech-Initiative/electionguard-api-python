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
    "KeyCeremonyGuardian",
    "KeyCeremonyGuardianStatus",
    "KeyCeremonyGuardianState",
]

PublicKeySet = Any

ElectionPartialKeyBackup = Any
ElectionPartialKeyVerification = Any
ElectionPartialKeyChallenge = Any


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

    key_name: str
    guardian_id: GUARDIAN_ID
    name: str
    sequence_order: int
    number_of_guardians: int
    quorum: int
    public_keys: Optional[PublicKeySet]
    backups: Optional[List[ElectionPartialKeyBackup]]
    verifications: Optional[List[ElectionPartialKeyVerification]]
    challenges: Optional[List[ElectionPartialKeyChallenge]]


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
