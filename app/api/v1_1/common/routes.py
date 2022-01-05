from fastapi import APIRouter
from . import ping

router = APIRouter()

router.include_router(ping.router, prefix="/ping")
