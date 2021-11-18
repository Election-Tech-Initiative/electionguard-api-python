from typing import Any, List
import sys
from fastapi import HTTPException, status

from .repository import get_repository, DataCollection
from .settings import Settings
from ..api.v1.models import BaseResponse, CiphertextTally, PlaintextTally

__all__ = [
    "ciphertext_tally_from_query",
    "plaintext_tally_from_query",
    "get_ciphertext_tally",
    "set_ciphertext_tally",
    "filter_ciphertext_tallies",
    "get_plaintext_tally",
    "set_plaintext_tally",
    "update_plaintext_tally",
    "filter_plaintext_tallies",
]


def ciphertext_tally_from_query(query_result: Any) -> CiphertextTally:
    return CiphertextTally(
        election_id=query_result["election_id"],
        tally_name=query_result["tally_name"],
        created=query_result["created"],
        tally=query_result["tally"],
    )


def plaintext_tally_from_query(query_result: Any) -> PlaintextTally:
    return PlaintextTally(
        election_id=query_result["election_id"],
        tally_name=query_result["tally_name"],
        created=query_result["created"],
        state=query_result["state"],
        tally=query_result["tally"],
    )


def get_ciphertext_tally(
    election_id: str, tally_name: str, settings: Settings = Settings()
) -> CiphertextTally:
    try:
        with get_repository(
            election_id, DataCollection.CIPHERTEXT_TALLY, settings
        ) as repository:
            query_result = repository.get(
                {"election_id": election_id, "tally_name": tally_name}
            )
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find tally {election_id} {tally_name}",
                )
            return ciphertext_tally_from_query(query_result)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{election_id} {tally_name} not found",
        ) from error


def set_ciphertext_tally(
    tally: CiphertextTally, settings: Settings = Settings()
) -> BaseResponse:
    try:
        with get_repository(
            tally.election_id, DataCollection.CIPHERTEXT_TALLY, settings
        ) as repository:
            repository.set(tally.dict())
            return BaseResponse()
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="set ciphertext tally failed",
        ) from error


def filter_ciphertext_tallies(
    election_id: str,
    filter: Any,
    skip: int = 0,
    limit: int = 1000,
    settings: Settings = Settings(),
) -> List[CiphertextTally]:
    try:
        with get_repository(
            election_id, DataCollection.CIPHERTEXT_TALLY, settings
        ) as repository:
            cursor = repository.find(filter, skip, limit)
            tallies: List[CiphertextTally] = []
            for item in cursor:
                tallies.append(ciphertext_tally_from_query(item))
            return tallies
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="filter ciphertext tallies failed",
        ) from error


def get_plaintext_tally(
    election_id: str, tally_name: str, settings: Settings = Settings()
) -> PlaintextTally:
    try:
        with get_repository(
            election_id, DataCollection.PLAINTEXT_TALLY, settings
        ) as repository:
            query_result = repository.get(
                {"election_id": election_id, "tally_name": tally_name}
            )
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find tally {election_id} {tally_name}",
                )
            return plaintext_tally_from_query(query_result)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="get plaintext tally failed",
        ) from error


def set_plaintext_tally(
    tally: PlaintextTally, settings: Settings = Settings()
) -> BaseResponse:
    try:
        with get_repository(
            tally.election_id, DataCollection.PLAINTEXT_TALLY, settings
        ) as repository:
            repository.set(tally.dict())
            return BaseResponse()
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="set plaintext tally failed",
        ) from error


def update_plaintext_tally(
    tally: PlaintextTally, settings: Settings = Settings()
) -> BaseResponse:
    try:
        with get_repository(
            tally.election_id, DataCollection.PLAINTEXT_TALLY, settings
        ) as repository:
            query_result = repository.get(
                {"election_id": tally.election_id, "tally_name": tally.tally_name}
            )
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find plaintext tally {tally.election_id} {tally.tally_name}",
                )
            repository.update(
                {"election_id": tally.election_id, "tally_name": tally.tally_name},
                tally.dict(),
            )
            return BaseResponse()
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="update plaintext tally failed",
        ) from error


def filter_plaintext_tallies(
    election_id: str,
    filter: Any,
    skip: int = 0,
    limit: int = 1000,
    settings: Settings = Settings(),
) -> List[PlaintextTally]:
    try:
        with get_repository(
            election_id, DataCollection.PLAINTEXT_TALLY, settings
        ) as repository:
            cursor = repository.find(filter, skip, limit)
            tallies: List[PlaintextTally] = []
            for item in cursor:
                tallies.append(plaintext_tally_from_query(item))
            return tallies
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="filter plaintext tallies failed",
        ) from error
