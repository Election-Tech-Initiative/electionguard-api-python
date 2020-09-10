from typing import Any

from .base import Base


class AcceptBallotRequest(Base):
    ballot: Any
    description: Any
    context: Any
