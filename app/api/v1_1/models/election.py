from typing import Any, List, Optional
from enum import Enum

from .base import Base, BaseRequest, BaseResponse


__all__ = [
    "CreateElectionRequest",
]

CiphertextElectionContext = Any


class CreateElectionRequest(BaseRequest):
    """Create an election."""

    name: str
