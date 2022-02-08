from typing import Any, List, Optional
from enum import Enum

from pydantic import BaseModel

from .base import BaseRequest, BaseResponse

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


class CreateUserResponse(BaseResponse):
    user_info: UserInfo
    password: str


class UserQueryRequest(BaseRequest):
    """A request for users using the specified filter."""

    filter: Optional[Any] = None
    """
    a json object filter that will be applied to the search.  Leave empty to retrieve all users.
    """

    class Config:
        schema_extra = {"example": {"filter": {"name": "Jane Doe"}}}


class UserQueryResponse(BaseModel):
    """Returns a collection of Users."""

    users: List[UserInfo]
