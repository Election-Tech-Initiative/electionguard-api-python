from typing import Any, List
import sys
from fastapi import HTTPException, status

from .client import get_client_id
from .repository import get_repository, DataCollection
from .settings import Settings
from ..api.v1.models import BaseResponse, UserInfo

__all__ = ["get_user_info", "filter_user_info", "set_user_info", "update_user_info"]


def get_user_info(username: str, settings: Settings = Settings()) -> UserInfo:
    try:
        with get_repository(
            get_client_id(), DataCollection.USER_INFO, settings
        ) as repository:
            query_result = repository.get({"username": username})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find user {username}",
                )
            return UserInfo(**query_result)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{username} not found",
        ) from error


def filter_user_info(
    filter: Any, skip: int = 0, limit: int = 1000, settings: Settings = Settings()
) -> List[UserInfo]:
    try:
        with get_repository(
            get_client_id(), DataCollection.ELECTION, settings
        ) as repository:
            cursor = repository.find(filter, skip, limit)
            results: List[UserInfo] = []
            for item in cursor:
                results.append(item)
            return results
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="filter users failed",
        ) from error


def set_user_info(user: UserInfo, settings: Settings = Settings()) -> None:
    try:
        with get_repository(
            get_client_id(), DataCollection.USER_INFO, settings
        ) as repository:
            query_result = repository.get({"username": user.username})
            if not query_result:
                repository.set(user.dict())
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Already exists {user.username}",
                )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="set user info failed",
        ) from error


def update_user_info(user: UserInfo, settings: Settings = Settings()) -> BaseResponse:
    try:
        with get_repository(
            get_client_id(), DataCollection.GUARDIAN, settings
        ) as repository:
            query_result = repository.get({"username": user.username})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find user {user.username}",
                )
            repository.update({"username": user.username}, user.dict())
            return BaseResponse()
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="update user info failed",
        ) from error
