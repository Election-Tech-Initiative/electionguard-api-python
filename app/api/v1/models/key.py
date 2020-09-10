from typing import Any, List, Optional

from .base import Base

ElectionPublicKey = str


class AuxiliaryKeyPair(Base):
    """Auxiliary pair of a secret key and public key."""

    secret_key: str
    public_key: str


class AuxiliaryPublicKey(Base):
    """Auxiliary public key and owner information"""

    owner_id: str
    sequence_order: int
    key: str


class ElectionKeyPair(Base):
    """Election key pair, proof and polynomial"""

    secret_key: str
    public_key: str
    proof: Any
    polynomial: Any


class ElectionKeyPairRequest(Base):
    quorum: int
    nonce: Optional[str] = None


class CombineElectionKeysRequest(Base):
    election_public_keys: List[ElectionPublicKey]


class ElectionJointKey(Base):
    joint_key: str
