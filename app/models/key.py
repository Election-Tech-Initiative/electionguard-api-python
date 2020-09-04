from typing import Any, Optional

from .base import Base


class AuxiliaryKeyPair(Base):
    secret_key: str
    public_key: str


class AuxiliaryPublicKey(Base):
    owner_id: str
    sequence_order: int
    key: str


class ElectionKeyPair(Base):
    secret_key: str
    public_key: str
    proof: Any
    polynomial: Any


class ElectionKeyPairRequest(Base):
    quorum: int
    nonce: Optional[str] = None
