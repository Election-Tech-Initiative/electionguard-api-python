from typing import Any

from .base import BaseRequest


__all__ = [
    "CreateElectionRequest",
]

CiphertextElectionContext = Any


class CreateElectionRequest(BaseRequest):
    """Create an election."""

    name: str
