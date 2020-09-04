from typing import Any

from .base import Base


class ElectionKeyPair(Base):
    secret_key: str
    public_key: str
    proof: Any
    polynomial: Any
