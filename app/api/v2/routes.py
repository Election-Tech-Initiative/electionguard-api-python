from fastapi import APIRouter
from app.api.v1 import auth
from app.core.settings import ApiMode, Settings
from . import common
from . import mediator


def get_v2_routes(settings: Settings) -> APIRouter:
    api_router = APIRouter()

    api_router.include_router(auth.router)

    if settings.API_MODE == ApiMode.GUARDIAN:
        raise ValueError(f"Guardian endpoints are  currently only available in v1")
    elif settings.API_MODE == ApiMode.MEDIATOR:
        api_router.include_router(mediator.router)
    else:
        raise ValueError(f"Unknown API mode: {settings.API_MODE}")

    api_router.include_router(common.router)

    return api_router
