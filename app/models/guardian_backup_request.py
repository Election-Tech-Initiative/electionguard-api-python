from typing import Any, List

from .auxiliary_public_key import AuxiliaryPublicKey
from .base import Base


class GuardianBackupRequest(Base):
    guardian_id: str
    quorum: int
    election_polynomial: Any

    auxiliary_public_keys: List[AuxiliaryPublicKey]
    """
    Auxiliary public keys for other guardians
    """
