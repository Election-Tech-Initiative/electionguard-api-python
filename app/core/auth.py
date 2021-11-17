import sys
from typing import Any, Union
from fastapi import HTTPException, status

from passlib.context import CryptContext

from .client import get_client_id
from .repository import get_repository, DataCollection
from .settings import Settings
from ..api.v1.models import BaseResponse, AuthenticationCredential

__all__ = [
    "AuthenticationContext",
    "get_auth_credential",
    "set_auth_credential",
    "update_auth_credential",
]


class AuthenticationContext:
    """
    An Authentication context object wrapper
    encapsulating the crypto context used to verify crdentials
    """

    def __init__(self, settings: Settings = Settings()):
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.settings = settings

    def authenticate_credential(self, username: str, password: str) -> Any:
        credential = get_auth_credential(username, self.settings)
        return self.verify_password(password, credential.hashed_password)

    def verify_password(self, plain_password: str, hashed_password: str) -> Any:
        return self.context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: Union[bytes, str]) -> Any:
        return self.context.hash(password)


def get_auth_credential(
    username: str, settings: Settings = Settings()
) -> AuthenticationCredential:
    """Get an authenitcation credential from the repository."""
    try:
        with get_repository(
            get_client_id(), DataCollection.AUTHENTICATION, settings
        ) as repository:
            query_result = repository.get({"username": username})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find credential for {username}",
                )
            return AuthenticationCredential(**query_result)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{username} not found",
        ) from error


def set_auth_credential(
    credential: AuthenticationCredential, settings: Settings = Settings()
) -> None:
    """Set an authentication credential in the repository."""
    try:
        with get_repository(
            get_client_id(), DataCollection.AUTHENTICATION, settings
        ) as repository:
            query_result = repository.get({"username": credential.username})
            if not query_result:
                repository.set(credential.dict())
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Already exists {credential.username}",
                )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="set auth credential failed",
        ) from error


def update_auth_credential(
    credential: AuthenticationCredential, settings: Settings = Settings()
) -> BaseResponse:
    """Update an authentication credential in the repository."""
    try:
        with get_repository(
            get_client_id(), DataCollection.AUTHENTICATION, settings
        ) as repository:
            query_result = repository.get({"username": credential.username})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find credential {credential.username}",
                )
            repository.update({"username": credential.username}, credential.dict())
            return BaseResponse()
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="update auth credential failed",
        ) from error
