from typing import Any, List, Optional

from .base import Base

__all__ = [
    "ElectionPublicKey",
    "AuxiliaryKeyPair",
    "AuxiliaryPublicKey",
    "ElectionKeyPair",
    "ElectionKeyPairRequest",
    "CombineElectionKeysRequest",
    "ElectionJointKey",
    "AuxiliaryRequest",
]

ElectionPublicKey = Any
ElGamalKeyPair = Any


class AuxiliaryKeyPair(Base):
    """Auxiliary pair of a secret key and public key."""

    owner_id: str
    sequence_order: int
    secret_key: str
    public_key: str


class AuxiliaryPublicKey(Base):
    """Auxiliary public key and owner information"""

    owner_id: str
    sequence_order: int
    key: str


class ElectionKeyPair(Base):
    """Election key pair, proof and polynomial"""

    owner_id: str
    sequence_order: int
    key_pair: ElGamalKeyPair
    polynomial: Any


class ElectionKeyPairRequest(Base):

    owner_id: str
    sequence_order: int
    quorum: int
    nonce: Optional[str] = None


class CombineElectionKeysRequest(Base):
    election_public_keys: List[ElectionPublicKey]


class ElectionJointKey(Base):
    joint_key: str


class AuxiliaryRequest(Base):
    owner_id: str
    sequence_order: int
