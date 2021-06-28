from typing import Any
import sys
from fastapi import HTTPException, status

from electionguard.serializable import write_json_object

from .client import get_client_id
from .repository import get_repository, DataCollection
from .settings import Settings
from ..api.v1.models import (
    BaseResponse,
    Guardian,
)


def from_query(query_result: Any) -> Guardian:
    return Guardian(
        guardian_id=query_result["guardian_id"],
        sequence_order=query_result["sequence_order"],
        number_of_guardians=query_result["number_of_guardians"],
        quorum=query_result["quorum"],
        election_keys=write_json_object(query_result["election_keys"]),
        auxiliary_keys=write_json_object(query_result["auxiliary_keys"]),
        backups=query_result["backups"],
        cohort_public_keys=query_result["cohort_public_keys"],
        cohort_backups=query_result["cohort_backups"],
        cohort_verifications=query_result["cohort_verifications"],
        cohort_challenges=query_result["cohort_challenges"],
    )


def get_guardian(guardian_id: str, settings: Settings = Settings()) -> Guardian:
    try:
        with get_repository(
            get_client_id(), DataCollection.GUARDIAN, settings
        ) as repository:
            query_result = repository.get({"guardian_id": guardian_id})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find guardian {guardian_id}",
                )
            guardian = from_query(query_result)
            return guardian
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="get guardian failed",
        ) from error


def update_guardian(
    guardian_id: str, guardian: Guardian, settings: Settings = Settings()
) -> BaseResponse:
    try:
        with get_repository(
            get_client_id(), DataCollection.GUARDIAN, settings
        ) as repository:
            query_result = repository.get({"guardian_id": guardian_id})
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
            detail="update guardian failed",
        ) from error
