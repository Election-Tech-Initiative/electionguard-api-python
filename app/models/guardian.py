from .base import Base
from .auxiliary_key_pair import AuxiliaryKeyPair
from .election_key_pair import ElectionKeyPair


class Guardian(Base):
    id: str
    sequence_order: int
    number_of_guardians: int
    quorum: int
    election_key_pair: ElectionKeyPair
    auxiliary_key_pair: AuxiliaryKeyPair
