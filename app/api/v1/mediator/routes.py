from fastapi import APIRouter
from . import ballot
from . import election
from . import key
from . import tally
from . import tracker

router = APIRouter()

router.include_router(election.router, prefix="/election")
router.include_router(key.router, prefix="/key")
router.include_router(ballot.router, prefix="/ballot")
router.include_router(tally.router, prefix="/tally")
router.include_router(tracker.router, prefix="/tracker")
