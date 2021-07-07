from typing import Any, List, Optional, Tuple

import sys
from fastapi import HTTPException, status

from electionguard.serializable import write_json_object

from .client import get_client_id
from .repository import get_repository, DataCollection
from .settings import Settings
from ..api.v1.models import BaseResponse, Election, ElectionState


def from_query(query_result: Any) -> Election:
    return Election(
        election_id=query_result["election_id"],
        state=query_result["state"],
        context=query_result["context"],
        manifest=query_result["manifest"],
    )


def get_election(election_id: str, settings: Settings = Settings()) -> Election:
    try:
        with get_repository(
            get_client_id(), DataCollection.ELECTION, settings
        ) as repository:
            query_result = repository.get({"election_id": election_id})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find election {election_id}",
                )
            election = from_query(query_result)

            return election
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="get election failed",
        ) from error


def set_election(election: Election, settings: Settings = Settings()) -> BaseResponse:
    try:
        with get_repository(
            get_client_id(), DataCollection.ELECTION, settings
        ) as repository:
            _ = repository.set(write_json_object(election.dict()))
            return BaseResponse(
                message="Election Successfully Set",
            )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Submit election failed",
        ) from error


def update_election_state(election_id: str, new_state: ElectionState) -> BaseResponse:
    try:
        with get_repository(get_client_id(), DataCollection.ELECTION) as repository:
            query_result = repository.get({"election_id": election_id})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find election {election_id}",
                )
            election = from_query(query_result)
            election.state = new_state
            repository.update({"election_id": election_id}, election.dict())
            return BaseResponse()
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="update election failed",
        ) from error
