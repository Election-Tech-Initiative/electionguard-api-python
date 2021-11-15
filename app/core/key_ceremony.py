from typing import Any
import sys
from fastapi import HTTPException, status

from .client import get_client_id
from .repository import get_repository, DataCollection
from .settings import Settings
from ..api.v1.models import (
    BaseResponse,
    KeyCeremony,
    KeyCeremonyState,
    KeyCeremonyGuardianStatus,
)


def from_query(query_result: Any) -> KeyCeremony:
    return KeyCeremony(
        key_name=query_result["key_name"],
        state=query_result["state"],
        number_of_guardians=query_result["number_of_guardians"],
        quorum=query_result["quorum"],
        guardian_ids=query_result["guardian_ids"],
        guardian_status=query_result["guardian_status"],
        elgamal_public_key=query_result["elgamal_public_key"],
        commitment_hash=query_result["commitment_hash"],
    )


def get_key_ceremony(key_name: str, settings: Settings = Settings()) -> KeyCeremony:
    try:
        with get_repository(
            get_client_id(), DataCollection.KEY_CEREMONY, settings
        ) as repository:
            query_result = repository.get({"key_name": key_name})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find key ceremony {key_name}",
                )
            key_ceremony = from_query(query_result)
            return key_ceremony
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{key_name} not found",
        ) from error


def update_key_ceremony(
    key_name: str, ceremony: KeyCeremony, settings: Settings = Settings()
) -> BaseResponse:
    try:
        with get_repository(
            get_client_id(), DataCollection.KEY_CEREMONY, settings
        ) as repository:
            query_result = repository.get({"key_name": key_name})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find key ceremony {key_name}",
                )
            repository.update({"key_name": key_name}, ceremony.dict())
            return BaseResponse()
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="update key ceremony failed",
        ) from error


def update_key_ceremony_state(
    key_name: str, new_state: KeyCeremonyState, settings: Settings = Settings()
) -> BaseResponse:
    try:
        with get_repository(
            get_client_id(), DataCollection.KEY_CEREMONY, settings
        ) as repository:
            query_result = repository.get({"key_name": key_name})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find key ceremony {key_name}",
                )
            key_ceremony = from_query(query_result)
            key_ceremony.state = new_state

            repository.update({"key_name": key_name}, key_ceremony.dict())
            return BaseResponse()
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="update key ceremony state failed",
        ) from error


def validate_can_publish(ceremony: KeyCeremony) -> None:
    # TODO: better validation
    for guardian_id, state in ceremony.guardian_status.items():
        if (
            state.public_key_shared != KeyCeremonyGuardianStatus.COMPLETE
            or state.backups_shared != KeyCeremonyGuardianStatus.COMPLETE
            or state.backups_verified != KeyCeremonyGuardianStatus.COMPLETE
        ):
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail=f"Publish constraint not satisfied for {guardian_id}",
            )
