from fastapi import APIRouter
from . import guardian
from . import key
from . import tally

router = APIRouter()

router.include_router(guardian.router, prefix="/guardian")
router.include_router(key.router, prefix="/key")
router.include_router(tally.router, prefix="/tally")
