from fastapi import APIRouter

from app.api.v1.endpoints import ballot, election, key, ping, tally

api_router = APIRouter()
api_router.include_router(ping.router, prefix="/ping", tags=["ping"])
api_router.include_router(election.router, prefix="/election", tags=["election"])
api_router.include_router(ballot.router, prefix="/ballot", tags=["ballot"])
api_router.include_router(key.router, prefix="/key", tags=["key"])
api_router.include_router(tally.router, prefix="/tally", tags=["tally"])
