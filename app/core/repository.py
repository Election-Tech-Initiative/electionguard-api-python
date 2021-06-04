from typing import Dict, Protocol, Any, List, Union
from collections.abc import MutableMapping

from pymongo import MongoClient
from pymongo.database import Database

from .settings import Settings, StorageMode

__all__ = ["IRepository", "MemoryRepository", "MongoRepository", "get_repository"]

settings = Settings()

DOCUMENT_VALUE_TYPE = Union[MutableMapping, List[MutableMapping]]


class IRepository(Protocol):
    def __enter__(self) -> Any:
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        pass

    def find(self, filter: MutableMapping, skip: int = 0, limit: int = 0) -> Any:
        """
        Find items matching the filter
        """

    def get(self, filter: MutableMapping) -> Any:
        """
        Get an item from the container
        """

    def set(self, value: DOCUMENT_VALUE_TYPE) -> Any:
        """
        Set and item in the container
        """

    def update(self, filter: MutableMapping, value: DOCUMENT_VALUE_TYPE) -> Any:
        """
        Update an item
        """


class DataCollection:
    GUARDIAN = "Guardian"
    ELECTION = "Election"
    MANIFEST = "Manifest"
    SUBMITTED_BALLOT = "SubmittedBallots"
    TALLY = "Tally"


class MemoryRepository(IRepository):
    def __init__(
        self,
        container: str,
        collection: str,
    ):
        super().__init__()
        self._id = 0
        self._container = container
        self._collection = collection
        self.storage: Dict[int, Any] = {}

    def __enter__(self) -> Any:
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        pass

    def find(self, filter: MutableMapping, skip: int = 0, limit: int = 0) -> Any:
        pass

    def get(self, filter: MutableMapping) -> Any:
        for item in self.storage.items():
            if item[filter[0]] == filter[1]:
                return item
        return None

    def set(self, value: DOCUMENT_VALUE_TYPE) -> Any:
        self._id += 1
        self.storage[self._id] = value
        return str(self._id)

    def update(self, filter: MutableMapping, value: DOCUMENT_VALUE_TYPE) -> Any:
        pass


class MongoRepository(IRepository):
    def __init__(
        self,
        uri: str,
        container: str,
        collection: str,
    ):
        super().__init__()
        self._uri = uri
        self._container = container
        self._collection = collection
        self._client: MongoClient = None
        self._database: Database = None

    def __enter__(self) -> Any:
        self._client = MongoClient(self._uri)
        self._database = self._client.get_database(self._container)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        self._client.close()

    def find(self, filter: MutableMapping, skip: int = 0, limit: int = 0) -> Any:
        collection = self._database.get_collection(self._collection)
        return collection.find(filter=filter, skip=skip, limit=limit)

    def get(self, filter: MutableMapping) -> Any:
        collection = self._database.get_collection(self._collection)
        return collection.find_one(filter)

    def set(self, value: DOCUMENT_VALUE_TYPE) -> Any:
        collection = self._database.get_collection(self._collection)
        if isinstance(value, List):
            result = collection.insert_many(value)
            return [str(id) for id in result.inserted_ids]
        result = collection.insert_one(value)
        return [str(result.inserted_id)]

    def update(self, filter: MutableMapping, value: DOCUMENT_VALUE_TYPE) -> Any:
        collection = self._database.get_collection(self._collection)
        return collection.update_one(filter=filter, update={"$set": value})


def get_repository(container: str, collection: str) -> IRepository:
    if settings.STORAGE_MODE == StorageMode.MONGO:
        return MongoRepository(settings.MONGODB_URI, container, collection)

    return MemoryRepository(container, collection)
