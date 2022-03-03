from typing import Any

from .base import BaseRequest


__all__ = [
    "CreateElectionRequest",
]

AnyCiphertextElectionContext = Any


class CreateElectionRequest(BaseRequest):
    """Create an election."""

    name: str
