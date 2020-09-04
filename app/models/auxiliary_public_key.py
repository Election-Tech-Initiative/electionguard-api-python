from .base import Base


class AuxiliaryPublicKey(Base):
    owner_id: str
    sequence_order: int
    key: str
