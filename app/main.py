import logging.config
from typing import Optional
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from app.api.v1.models.auth import AuthenticationCredential


from app.api.v1.routes import get_v1_routes
from app.api.v1_1.routes import get_v1_1_routes
from app.core.settings import Settings
from app.core.scheduler import get_scheduler

from app.api.v1.models import UserInfo, UserScope
from app.core import AuthenticationContext, set_auth_credential, set_user_info

# setup loggers
logging.config.fileConfig("app/logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def seed_default_user(settings: Settings = Settings()) -> None:
    # TODO: a more secure way to set the default auth credential
    hashed_password = AuthenticationContext(settings).get_password_hash(
        settings.DEFAULT_ADMIN_PASSWORD
    )
    credential = AuthenticationCredential(
        username=settings.DEFAULT_ADMIN_USERNAME, hashed_password=hashed_password
    )
    user_info = UserInfo(
        username=credential.username,
        first_name=credential.username,
        last_name=credential.username,
        scopes=[UserScope.admin],
    )
    try:
        set_auth_credential(credential, settings)
    except HTTPException:
        pass

    try:
        set_user_info(user_info, settings)
    except HTTPException:
        pass


def get_app(settings: Optional[Settings] = None) -> FastAPI:
    if not settings:
        settings = Settings()

    web_app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        version="1.0.5",
    )

    web_app.state.settings = settings

    logger.info(f"Starting API in {web_app.state.settings.API_MODE} mode")

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        web_app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    seed_default_user(settings)

    v1_routes = get_v1_routes(settings)
    web_app.include_router(v1_routes, prefix=settings.API_V1_STR)
    v1_1_routes = get_v1_1_routes(settings)
    web_app.include_router(v1_1_routes, prefix=settings.API_V1_1_STR)

    return web_app


app = get_app()


@app.on_event("startup")
def on_startup() -> None:
    pass


@app.on_event("shutdown")
def on_shutdown() -> None:
    # Ensure a clean shutdown of the singleton Scheduler
    scheduler = get_scheduler()
    scheduler.close()


if __name__ == "__main__":
    # IMPORTANT: This should only be used to debug the application.
    # For normal execution, run `make start`.
    #
    # To make this work, the PYTHONPATH must be set to the root directory, e.g.
    # `PYTHONPATH=. poetry run python ./app/main.py`
    # See the VSCode launch configuration for detail.
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--port",
        default=8000,
        type=int,
        help="The port to listen on",
    )
    args = parser.parse_args()

    uvicorn.run(app, host="0.0.0.0", port=args.port)
