from typing import Any, List, Optional

from .base import Base
from .key import AuxiliaryKeyPair, AuxiliaryPublicKey, ElectionKeyPair


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


class GuardianBackup(Base):
    id: str
    election_partial_key_backups: List[Any]


class GuardianBackupRequest(Base):
    guardian_id: str
    quorum: int
    election_polynomial: Any

    auxiliary_public_keys: List[AuxiliaryPublicKey]
    """
    Auxiliary public keys for other guardians
    """
