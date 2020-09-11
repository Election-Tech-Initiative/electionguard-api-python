from fastapi import APIRouter
from app.core.config import settings, ApiMode
from . import common

api_router = APIRouter()

if settings.API_MODE == ApiMode.guardian:
    from . import guardian

    api_router.include_router(guardian.router)
elif settings.API_MODE == ApiMode.mediator:
    from . import mediator

    api_router.include_router(mediator.router)
else:
    raise ValueError(f"Unknown API mode: {settings.API_MODE}")


api_router.include_router(common.router)
