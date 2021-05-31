from typing import List
from enum import Enum
from pydantic import AnyHttpUrl, BaseSettings
from pydantic.fields import Field


class ApiMode(str, Enum):
    GUARDIAN = "guardian"
    MEDIATOR = "mediator"


class QueueMode(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"


class StorageMode(str, Enum):
    LOCAL_STORAGE = "local_storage"
    MEMORY = "memory"
    MONGO = "mongo"


# pylint:disable=too-few-public-methods
class Settings(BaseSettings):
    API_MODE: ApiMode = ApiMode.MEDIATOR
    QUEUE_MODE: QueueMode = QueueMode.LOCAL
    STORAGE_MODE: StorageMode = StorageMode.MEMORY
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=["http://localhost", "http://localhost:8080", "https://localhost"]
    )
    PROJECT_NAME: str = "electionguard-api-python"
    MONGODB_URI: str = "mongodb://root:example@mongo:27017"
    MESSAGEQUEUE_URI: str = "amqp://guest:guest@localhost:5672"

    class Config:
        case_sensitive = True
