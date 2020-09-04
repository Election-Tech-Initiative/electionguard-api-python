from typing import Optional

from .base import Base


class ElectionKeyPairRequest(Base):
    quorum: int
    nonce: Optional[str] = None
