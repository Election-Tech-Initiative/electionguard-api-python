from fastapi import APIRouter, Body, Request

from ..models import (
    BaseResponse,
    CreateElectionRequest,
)
from ..tags import ELECTION

router = APIRouter()


@router.put("", response_model=BaseResponse, tags=[ELECTION])
def create_election(
    request: Request,
    data: CreateElectionRequest = Body(...),
) -> BaseResponse:
    """
    1. Create an election

    Takes only an optional name parameter and returns a surrogate key so that
    users can subsequently add a manifest and key to it prior to opening the
    election.
    """

    return BaseResponse(
        message=f"This endpoint isn't yet implemented, but eventually it will add the '{data.name}' election",
    )
