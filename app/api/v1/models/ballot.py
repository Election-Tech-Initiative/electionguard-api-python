from typing import Any

from .base import Base
from .election import ElectionDecription, CiphertextElectionContext


CiphertextAcceptedBallot = Any
CiphertextBallot = Any


class AcceptBallotRequest(Base):
    ballot: CiphertextBallot
    description: ElectionDecription
    context: CiphertextElectionContext
