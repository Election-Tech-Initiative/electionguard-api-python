from fastapi import APIRouter
from app.core.config import ApiMode, Settings
from . import common
from . import guardian
from . import mediator


def get_routes(settings: Settings) -> APIRouter:
    api_router = APIRouter()

    if settings.API_MODE == ApiMode.GUARDIAN:
        api_router.include_router(guardian.router)
    elif settings.API_MODE == ApiMode.MEDIATOR:
        api_router.include_router(mediator.router)
    else:
        raise ValueError(f"Unknown API mode: {settings.API_MODE}")

    api_router.include_router(common.router)

    return api_router
