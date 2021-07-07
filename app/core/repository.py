from typing import Dict, Protocol, Any, List, Union
from collections.abc import MutableMapping

import mmap
import os
import json
import re

from pymongo import MongoClient
from pymongo.database import Database

from electionguard.hash import hash_elems

from .settings import Settings, StorageMode

__all__ = [
    "IRepository",
    "LocalRepository",
    "MemoryRepository",
    "MongoRepository",
    "get_repository",
]


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
    GUARDIAN = "guardian"
    KEY_GUARDIAN = "keyGuardian"
    KEY_CEREMONY = "keyCeremony"
    ELECTION = "election"
    MANIFEST = "manifest"
    BALLOT_INVENTORY = "ballotInventory"
    SUBMITTED_BALLOT = "submittedBallots"
    TALLY = "tally"


class LocalRepository(IRepository):
    """A simple local storage interface.  For testing only."""

    def __init__(
        self,
        container: str,
        collection: str,
    ):
        super().__init__()
        self._id = 0
        self._container = container
        self._collection = collection
        self._storage = os.path.join(
            os.getcwd(), "storage", self._container, self._collection
        )

    def __enter__(self) -> Any:
        if not os.path.exists(self._storage):
            os.makedirs(self._storage)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        pass

    def find(self, filter: MutableMapping, skip: int = 0, limit: int = 0) -> Any:
        # TODO: implement a find function
        pass

    def get(self, filter: MutableMapping) -> Any:
        """An inefficient search through all files in the directory."""
        # query_string = json.dumps(dict(filter))
        query_string = re.sub(r"\{|\}", r"", json.dumps(dict(filter)))

        search_files = [
            file
            for file in os.listdir(self._storage)
            if os.path.isfile(os.path.join(self._storage, file))
        ]

        for filename in search_files:
            try:
                with open(os.path.join(self._storage, filename)) as file, mmap.mmap(
                    file.fileno(), 0, access=mmap.ACCESS_READ
                ) as search:
                    if search.find(bytes(query_string, "utf-8")) != -1:
                        json_string = file.read()
                        return json.loads(json_string)
            except FileNotFoundError:
                # swallow errors
                pass
        return None

    def set(self, value: DOCUMENT_VALUE_TYPE) -> Any:
        """A naive set function that hashes the data and writes the file."""
        # just ignore lists for now
        if isinstance(value, List):
            raise Exception("Not Implemented")
        json_string = json.dumps(dict(value))
        filename = hash_elems(json_string).to_hex()
        with open(f"{os.path.join(self._storage, filename)}.json", "w") as file:
            file.write(json_string)
        return filename

    def update(self, filter: MutableMapping, value: DOCUMENT_VALUE_TYPE) -> Any:
        # TODO: implement an update function
        pass


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


def get_repository(
    container: str, collection: str, settings: Settings = Settings()
) -> IRepository:
    """Get a repository by settings strage mode."""
    if settings.STORAGE_MODE == StorageMode.MONGO:
        return MongoRepository(settings.MONGODB_URI, container, collection)

    if settings.STORAGE_MODE == StorageMode.LOCAL_STORAGE:
        return LocalRepository(container, collection)

    return MemoryRepository(container, collection)
