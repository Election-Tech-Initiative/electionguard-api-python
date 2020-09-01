from pydantic import AnyHttpUrl, BaseSettings
from typing import cast, List


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = cast(
        List[AnyHttpUrl],
        ["http://localhost", "http://localhost:8080", "https://localhost"],
    )
    PROJECT_NAME: str = "electionguard-web-api"

    class Config:
        case_sensitive = True


settings = Settings()
