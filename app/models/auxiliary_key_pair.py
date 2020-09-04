from .base import Base


class AuxiliaryKeyPair(Base):
    secret_key: str
    public_key: str
