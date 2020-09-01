from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.get("", response_model=str)
def ping() -> Any:
    """
    Ensure API can be pinged
    """
    return "pong"
