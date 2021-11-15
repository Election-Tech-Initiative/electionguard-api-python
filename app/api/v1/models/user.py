from typing import List, Optional
from enum import Enum

from pydantic import BaseModel

__all__ = [
    "UserScope",
    "UserInfo",
]


class UserScope(str, Enum):
    admin = "admin"
    """The admin role can execute administrative functions."""
    auditor = "auditor"
    """The auditor role is a readonly role that can observe the election."""
    guardian = "guardian"
    """The guardian role can excute guardian functions."""
    voter = "voter"
    """
    The voter role can execute voting functions such as encrypt ballot.
    The voting endpoints are useful for testing only and are not recommended for production.
    """


class UserInfo(BaseModel):
    """A specific user in the system"""

    username: str
    scopes: List[UserScope] = []
    email: Optional[str] = None
    disabled: Optional[bool] = None
