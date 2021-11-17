from typing import Any, List
import sys
from fastapi import HTTPException, status

from .repository import get_repository, DataCollection
from .settings import Settings
from ..api.v1.models import BaseResponse, CiphertextTallyDecryptionShare


def from_tally_decryption_share_query(
    query_result: Any,
) -> CiphertextTallyDecryptionShare:
    return CiphertextTallyDecryptionShare(
        election_id=query_result["election_id"],
        tally_name=query_result["tally_name"],
        guardian_id=query_result["guardian_id"],
        tally_share=query_result["tally_share"],
        ballot_shares=query_result["ballot_shares"],
    )


def get_decryption_share(
    election_id: str, tally_name: str, guardian_id: str, settings: Settings = Settings()
) -> CiphertextTallyDecryptionShare:
    try:
        with get_repository(
            tally_name, DataCollection.DECRYPTION_SHARES, settings
        ) as repository:
            query_result = repository.get(
                {
                    "election_id": election_id,
                    "tally_name": tally_name,
                    "guardian_id": guardian_id,
                }
            )
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find decryption share {election_id} {tally_name} {guardian_id}",
                )
            return from_tally_decryption_share_query(query_result)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{election_id} {tally_name} {guardian_id} not found",
        ) from error


def set_decryption_share(
    decryption_share: CiphertextTallyDecryptionShare, settings: Settings = Settings()
) -> BaseResponse:
    try:
        with get_repository(
            decryption_share.tally_name, DataCollection.DECRYPTION_SHARES, settings
        ) as repository:
            repository.set(decryption_share.dict())
            return BaseResponse()
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="set decryption share failed",
        ) from error


def filter_decryption_shares(
    tally_name: str,
    filter: Any,
    skip: int = 0,
    limit: int = 1000,
    settings: Settings = Settings(),
) -> List[CiphertextTallyDecryptionShare]:
    try:
        with get_repository(
            tally_name, DataCollection.DECRYPTION_SHARES, settings
        ) as repository:
            cursor = repository.find(filter, skip, limit)
            decryption_shares: List[CiphertextTallyDecryptionShare] = []
            for item in cursor:
                decryption_shares.append(from_tally_decryption_share_query(item))
            return decryption_shares
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="find decryption shares failed",
        ) from error
