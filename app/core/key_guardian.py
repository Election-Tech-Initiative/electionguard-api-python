import sys
from fastapi import HTTPException, status

from electionguard.serializable import read_json_object

from .client import get_client_id
from .repository import get_repository, DataCollection
from ..api.v1.models import (
    BaseResponse,
    ResponseStatus,
    KeyCeremonyGuardian,
)


def get_key_guardian(key_name: str, guardian_id: str) -> KeyCeremonyGuardian:
    try:
        with get_repository(get_client_id(), DataCollection.KEY_GUARDIAN) as repository:
            query_result = repository.get(
                {"key_name": key_name, "guardian_id": guardian_id}
            )
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find guardian {guardian_id}",
                )
            guardian = KeyCeremonyGuardian(
                key_name=query_result["key_name"],
                guardian_id=query_result["guardian_id"],
                name=query_result["name"],
                sequence_order=query_result["sequence_order"],
                number_of_guardians=query_result["number_of_guardians"],
                quorum=query_result["quorum"],
                public_keys=query_result["public_keys"],
                backups=query_result["backups"],
                verifications=query_result["verifications"],
                challenges=query_result["challenges"],
            )
            return guardian
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="get key ceremony guardian failed",
        ) from error


def update_key_guardian(
    key_name: str, guardian_id: str, guardian: KeyCeremonyGuardian
) -> BaseResponse:
    try:
        with get_repository(get_client_id(), DataCollection.KEY_GUARDIAN) as repository:
            query_result = repository.get(
                {"key_name": key_name, "guardian_id": guardian_id}
            )
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find guardian {guardian_id}",
                )
            repository.update({"guardian_id": guardian_id}, guardian.dict())
            return BaseResponse()
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="update key ceremony guardian failed",
        ) from error