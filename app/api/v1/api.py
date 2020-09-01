from fastapi import APIRouter

from app.api.v1.endpoints import ballot, ping, election

api_router = APIRouter()
api_router.include_router(ping.router, prefix="/ping", tags=["ping"])
api_router.include_router(election.router, prefix="/election", tags=["election"])
api_router.include_router(ballot.router, prefix="/ballot", tags=["ballot"])
