from typing import Any, List
import sys
from electionguard.serializable import read_json_object, write_json_object

from fastapi import HTTPException, status

from electionguard.group import ElementModQ
import electionguard.manifest

from .client import get_client_id
from .repository import get_repository, DataCollection
from .settings import Settings
from ..api.v1.models import Manifest, ManifestSubmitResponse, ManifestQueryResponse

# TODO: rework the caching mechanism to reduce the amount of object conversions
def from_query(query_result: Any) -> Manifest:
    sdk_manifest = electionguard.manifest.Manifest.from_json_object(
        query_result["manifest"]
    )
    return Manifest(
        manifest_hash=write_json_object(sdk_manifest.crypto_hash()),
        manifest=write_json_object(sdk_manifest),
    )


def get_manifest(
    manifest_hash: ElementModQ, settings: Settings = Settings()
) -> Manifest:
    try:
        with get_repository(
            get_client_id(), DataCollection.MANIFEST, settings
        ) as repository:
            query_result = repository.get({"manifest_hash": manifest_hash.to_hex()})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find manifest {manifest_hash.to_hex()}",
                )

            return from_query(query_result)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="get manifest failed",
        ) from error


def set_manifest(
    manifest: Manifest, settings: Settings = Settings()
) -> ManifestSubmitResponse:
    try:
        with get_repository(
            get_client_id(), DataCollection.MANIFEST, settings
        ) as repository:
            manifest_hash = read_json_object(
                manifest.manifest_hash, ElementModQ
            ).to_hex()
            _ = repository.set(
                {"manifest_hash": manifest_hash, "manifest": manifest.manifest}
            )
            return ManifestSubmitResponse(manifest_hash=manifest_hash)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Submit manifest failed",
        ) from error


def filter_manifests(
    filter: Any, skip: int = 0, limit: int = 1000, settings: Settings = Settings()
) -> ManifestQueryResponse:
    try:
        with get_repository(
            get_client_id(), DataCollection.MANIFEST, settings
        ) as repository:
            cursor = repository.find(filter, skip, limit)
            manifests: List[Manifest] = []
            for item in cursor:
                manifests.append(from_query(item))
            return ManifestQueryResponse(manifests=manifests)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="find manifests failed",
        ) from error
