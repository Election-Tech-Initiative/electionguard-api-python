import sys
from fastapi import HTTPException, status

from electionguard.serializable import read_json_object

from .client import get_client_id
from .repository import get_repository, DataCollection
from ..api.v1.models import (
    BaseResponse,
    ResponseStatus,
    KeyCeremony,
    KeyCeremonyState,
    KeyCeremonyGuardianStatus,
)


def get_key_ceremony(key_name: str) -> KeyCeremony:
    try:
        with get_repository(get_client_id(), DataCollection.KEY_CEREMONY) as repository:
            query_result = repository.get({"guardian_id": key_name})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find guardian {key_name}",
                )

            return read_json_object(query_result, KeyCeremony)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="get key ceremony failed",
        ) from error


def update_key_ceremony(key_name: str, ceremony: KeyCeremony) -> BaseResponse:
    try:
        with get_repository(get_client_id(), DataCollection.KEY_CEREMONY) as repository:
            query_result = repository.get({"key_name": key_name})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find key ceremony {key_name}",
                )
            repository.update({"key_name": key_name}, ceremony.dict())
            return BaseResponse(status=ResponseStatus.SUCCESS)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="update election failed",
        ) from error


def update_key_ceremony_state(
    key_name: str, new_state: KeyCeremonyState
) -> BaseResponse:
    try:
        with get_repository(get_client_id(), DataCollection.KEY_CEREMONY) as repository:
            query_result = repository.get({"key_name": key_name})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find key ceremony {key_name}",
                )
            document = read_json_object(query_result, KeyCeremony)
            document.state = new_state

            repository.update({"key_name": key_name}, document.dict())
            return BaseResponse(status=ResponseStatus.SUCCESS)
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
                detail=f"Publish Constraint not satisfied for {guardian_id}",
            )