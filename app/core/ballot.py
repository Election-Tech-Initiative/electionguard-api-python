from typing import Any, List, Optional
import sys
from fastapi import HTTPException, status

from electionguard.ballot import (
    SubmittedBallot,
)

from .repository import get_repository, DataCollection
from .settings import Settings
from ..api.v1.models import BaseResponse, BallotInventory


__all__ = [
    "get_ballot",
    "set_ballots",
    "filter_ballots",
    "get_ballot_inventory",
    "upsert_ballot_inventory",
]


def get_ballot(
    election_id: str, ballot_id: str, settings: Settings = Settings()
) -> SubmittedBallot:
    try:
        with get_repository(
            election_id, DataCollection.SUBMITTED_BALLOT, settings
        ) as repository:
            query_result = repository.get({"object_id": ballot_id})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find ballot_id {ballot_id}",
                )
            return SubmittedBallot.from_json_object(query_result)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{ballot_id} not found",
        ) from error


def set_ballots(
    election_id: str, ballots: List[SubmittedBallot], settings: Settings = Settings()
) -> BaseResponse:
    try:
        with get_repository(
            election_id, DataCollection.SUBMITTED_BALLOT, settings
        ) as repository:
            cacheable_ballots = [ballot.to_json_object() for ballot in ballots]
            _ = repository.set(cacheable_ballots)
            return BaseResponse(
                message="Ballots Successfully Set",
            )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="set ballots failed",
        ) from error


def filter_ballots(
    election_id: str,
    filter: Any,
    skip: int = 0,
    limit: int = 1000,
    settings: Settings = Settings(),
) -> List[SubmittedBallot]:
    try:
        with get_repository(
            election_id, DataCollection.SUBMITTED_BALLOT, settings
        ) as repository:
            cursor = repository.find(filter, skip, limit)
            ballots: List[SubmittedBallot] = []
            for item in cursor:
                ballots.append(SubmittedBallot.from_json_object(item))
            return ballots
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="provided filter not found",
        ) from error


def get_ballot_inventory(
    election_id: str, settings: Settings = Settings()
) -> Optional[BallotInventory]:
    try:
        with get_repository(
            election_id, DataCollection.BALLOT_INVENTORY, settings
        ) as repository:
            query_result = repository.get({"election_id": election_id})
            if not query_result:
                return None
            return BallotInventory(
                election_id=query_result["election_id"],
                cast_ballot_count=query_result["cast_ballot_count"],
                spoiled_ballot_count=query_result["spoiled_ballot_count"],
                cast_ballots=query_result["cast_ballots"],
                spoiled_ballots=query_result["spoiled_ballots"],
            )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="get ballot inventory failed",
        ) from error


def upsert_ballot_inventory(
    election_id: str, inventory: BallotInventory, settings: Settings = Settings()
) -> BaseResponse:
    try:
        with get_repository(
            election_id, DataCollection.BALLOT_INVENTORY, settings
        ) as repository:
            query_result = repository.get({"election_id": election_id})
            if not query_result:
                repository.set(inventory.dict())
            else:
                repository.update({"election_id": election_id}, inventory.dict())
            return BaseResponse()
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="update ballot inventory failed",
        ) from error
