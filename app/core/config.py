from typing import List
from enum import Enum
from pydantic import AnyHttpUrl, BaseSettings
from pydantic.fields import Field


class ApiMode(str, Enum):
    GUARDIAN = "guardian"
    MEDIATOR = "mediator"


# pylint:disable=too-few-public-methods
class Settings(BaseSettings):
    API_MODE: ApiMode = ApiMode.MEDIATOR
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=["http://localhost", "http://localhost:8080", "https://localhost"]
    )
    PROJECT_NAME: str = "electionguard-api-python"

    class Config:
        case_sensitive = True
