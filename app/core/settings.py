from typing import List
from enum import Enum
from pydantic import AnyHttpUrl, BaseSettings
from pydantic.fields import Field

__all__ = [
    "ApiMode",
    "QueueMode",
    "StorageMode",
    "Settings",
]


class ApiMode(str, Enum):
    GUARDIAN = "guardian"
    MEDIATOR = "mediator"


class QueueMode(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"


class StorageMode(str, Enum):
    LOCAL_STORAGE = "local_storage"
    MONGO = "mongo"


# pylint:disable=too-few-public-methods
class Settings(BaseSettings):
    API_MODE: ApiMode = ApiMode.MEDIATOR
    QUEUE_MODE: QueueMode = QueueMode.LOCAL
    STORAGE_MODE: StorageMode = StorageMode.LOCAL_STORAGE

    API_V1_STR: str = "/api/v1"
    API_V1_1_STR: str = "/api/v1.1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=[
            "http://localhost",
            "http://localhost:8080",
            "http://localhost:6006",
            "http://localhost:3000",
            "https://localhost",
        ]
    )
    PROJECT_NAME: str = "electionguard-api-python"
    MONGODB_URI: str = "mongodb://root:example@localhost:27017"
    MESSAGEQUEUE_URI: str = "amqp://guest:guest@localhost:5672"

    AUTH_ALGORITHM = "HS256"
    AUTH_SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    DEFAULT_ADMIN_USERNAME = "default"
    DEFAULT_ADMIN_PASSWORD = "<this is a default value and should be changed>"
    # this is a default value that will be moving to the environment settings
    # the default value should not be used for production use

    class Config:
        case_sensitive = True
