import traceback
from typing import List
import sys
from fastapi import APIRouter, Body, HTTPException, Request, status

from electionguard.serializable import write_json_object, read_json_object

from ....core.client import get_client_id
from ....core.key_guardian import get_key_guardian, update_key_guardian
from ....core.repository import get_repository, DataCollection
from ..models import (
    BaseQueryRequest,
    BaseResponse,
    GuardianQueryResponse,
    KeyCeremonyGuardian,
)
from ..tags import KEY_GUARDIAN

router = APIRouter()


@router.get("", response_model=GuardianQueryResponse, tags=[KEY_GUARDIAN])
def fetch_key_ceremony_guardian(
    request: Request, key_name: str, guardian_id: str
) -> GuardianQueryResponse:
    """
    Get a key ceremony guardian.
    """
    guardian = get_key_guardian(key_name, guardian_id, request.app.state.settings)
    return GuardianQueryResponse(guardians=[guardian])


@router.put("", response_model=BaseResponse, tags=[KEY_GUARDIAN])
def create_key_ceremony_guardian(
    request: Request,
    data: KeyCeremonyGuardian = Body(...),
) -> BaseResponse:
    """
    Create a Key Ceremony Guardian.

    In order for a guardian to participate they must be associated with the key ceremony first.
    """
    try:
        with get_repository(
            get_client_id(), DataCollection.KEY_GUARDIAN, request.app.state.settings
        ) as repository:
            query_result = repository.get(
                {"key_name": data.key_name, "guardian_id": data.guardian_id}
            )
            if not query_result:
                repository.set(data.dict())
                return BaseResponse()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Already exists {data.guardian_id}",
            )
    except Exception as error:
        traceback.print_exc()
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Submit ballots failed",
        ) from error


@router.post("", response_model=BaseResponse, tags=[KEY_GUARDIAN])
def update_key_ceremony_guardian(
    request: Request,
    data: KeyCeremonyGuardian = Body(...),
) -> BaseResponse:
    """
    Update a Key Ceremony Guardian.

    This API is primarily for administrative purposes.
    """
    return update_key_guardian(
        data.key_name, data.guardian_id, data, request.app.state.settings
    )


@router.post("/find", response_model=GuardianQueryResponse, tags=[KEY_GUARDIAN])
def find_key_ceremony_guardians(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    data: BaseQueryRequest = Body(...),
) -> GuardianQueryResponse:
    """
    Find Guardians.

    Search the repository for guardians that match the filter criteria specified in the request body.
    If no filter criteria is specified the API will iterate all available data.
    """
    try:
        filter = write_json_object(data.filter) if data.filter else {}
        with get_repository(
            get_client_id(), DataCollection.KEY_GUARDIAN, request.app.state.settings
        ) as repository:
            cursor = repository.find(filter, skip, limit)
            guardians: List[KeyCeremonyGuardian] = []
            for item in cursor:
                guardians.append(read_json_object(item, KeyCeremonyGuardian))
            return GuardianQueryResponse(guardians=guardians)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="find guardians failed",
        ) from error
