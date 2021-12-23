from fastapi import APIRouter
from . import election

router = APIRouter()

router.include_router(election.router, prefix="/election")
