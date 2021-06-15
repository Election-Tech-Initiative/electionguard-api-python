from typing import List
import sys
from fastapi import APIRouter, Body, HTTPException, status

from electionguard.serializable import write_json_object, read_json_object

from ....core.client import get_client_id
from ....core.key_guardian import get_key_guardian
from ....core.repository import get_repository, DataCollection
from ..models import (
    BaseQueryRequest,
    BaseResponse,
    ResponseStatus,
    GuardianQueryResponse,
    KeyCeremonyGuardian,
)
from ..tags import GUARDIAN

router = APIRouter()


@router.get("", tags=[GUARDIAN])
def get_key_ceremony_guardian(guardian_id: str) -> GuardianQueryResponse:
    """
    Get a guardian.
    """
    guardian = get_key_guardian(guardian_id)
    return GuardianQueryResponse(status=ResponseStatus.SUCCESS, guardians=[guardian])


@router.put("", tags=[GUARDIAN])
def create_guardian(request: KeyCeremonyGuardian = Body(...)) -> BaseResponse:
    """
    Create a Key Ceremony Guardian.
    """
    try:
        with get_repository(get_client_id(), DataCollection.GUARDIAN) as repository:
            query_result = repository.get({"guardian_id": request.guardian_id})
            if not query_result:
                repository.set(request)
                return BaseResponse(status=ResponseStatus.SUCCESS)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Already exists {request.guardian_id}",
            )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Submit ballots failed",
        ) from error


@router.get("/find", tags=[GUARDIAN])
def find_key_ceremony_guardians(
    skip: int = 0, limit: int = 100, request: BaseQueryRequest = Body(...)
) -> GuardianQueryResponse:
    """
    Find Guardians.

    Search the repository for guardians that match the filter criteria specified in the request body.
    If no filter criteria is specified the API will iterate all available data.
    """
    try:
        filter = write_json_object(request.filter) if request.filter else {}
        with get_repository(get_client_id(), DataCollection.GUARDIAN) as repository:
            cursor = repository.find(filter, skip, limit)
            guardians: List[KeyCeremonyGuardian] = []
            for item in cursor:
                guardians.append(read_json_object(item, KeyCeremonyGuardian))
            return GuardianQueryResponse(
                status=ResponseStatus.SUCCESS, guardians=guardians
            )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="find guardians failed",
        ) from error
