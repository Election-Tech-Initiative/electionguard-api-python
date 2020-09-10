from typing import Any, List

from .base import Base


class StartTallyRequest(Base):
    ballots: List[Any]
    description: Any
    context: Any


class AppendTallyRequest(StartTallyRequest):
    encrypted_tally: Any
