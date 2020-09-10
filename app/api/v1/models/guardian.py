from typing import Any, List, Optional

from .base import Base
from .key import AuxiliaryKeyPair, AuxiliaryPublicKey, ElectionKeyPair

ElectionPolynomial = Any
ElectionPartialKeyBackup = Any
ElectionPartialKeyChallenge = Any


class Guardian(Base):
    id: str
    sequence_order: int
    number_of_guardians: int
    quorum: int
    election_key_pair: ElectionKeyPair
    auxiliary_key_pair: AuxiliaryKeyPair


class GuardianRequest(Base):
    id: str
    sequence_order: int
    number_of_guardians: int
    quorum: int
    nonce: Optional[str] = None
    auxiliary_key_pair: Optional[AuxiliaryKeyPair] = None


class GuardianBackup(Base):
    id: str
    election_partial_key_backups: List[ElectionPartialKeyBackup]


class GuardianBackupRequest(Base):
    guardian_id: str
    quorum: int
    election_polynomial: ElectionPolynomial
    auxiliary_public_keys: List[AuxiliaryPublicKey]
    override_rsa: bool = False


class BackupVerificationRequest(Base):
    verifier_id: str
    election_partial_key_backup: ElectionPartialKeyBackup
    auxiliary_key_pair: AuxiliaryKeyPair
    override_rsa: bool = False


class BackupChallengeRequest(Base):
    election_partial_key_backup: ElectionPartialKeyBackup
    election_polynomial: ElectionPolynomial


class ChallengeVerificationRequest(Base):
    verifier_id: str
    election_partial_key_challenge: ElectionPartialKeyChallenge
