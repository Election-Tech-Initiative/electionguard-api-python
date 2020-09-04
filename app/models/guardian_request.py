from typing import Optional

from .base import Base


class GuardianRequest(Base):
    id: str
    sequence_order: int
    number_of_guardians: int
    quorum: int
    nonce: Optional[str] = None
