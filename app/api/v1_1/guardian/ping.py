from typing import Any

from fastapi import APIRouter

from ..tags import UTILITY

router = APIRouter()


@router.get("", response_model=str, tags=[UTILITY])
def ping() -> Any:
    """
    Ensure API can be pinged
    """
    return "pong"
