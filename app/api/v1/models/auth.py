from typing import List, Optional

from pydantic import BaseModel

from app.api.v1.models.user import UserScope

__all__ = [
    "AuthenticationCredential",
    "Token",
    "TokenData",
]


class AuthenticationCredential(BaseModel):
    """Authentication credential used to authenticate users."""

    username: str
    hashed_password: str


class Token(BaseModel):
    """An access token and its type."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """The payload of an access token."""

    username: Optional[str] = None
    scopes: List[UserScope] = []
