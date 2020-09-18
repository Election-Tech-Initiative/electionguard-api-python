from logging import getLogger
from typing import Optional
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.routes import get_routes
from app.core.config import Settings

logger = getLogger(__name__)


def get_app(settings: Optional[Settings] = None) -> FastAPI:
    if not settings:
        settings = Settings()

    web_app = FastAPI(
        title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    logger.error(f"Starting API in {settings.API_MODE} mode")

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        web_app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    routes = get_routes(settings)
    web_app.include_router(routes, prefix=settings.API_V1_STR)

    return web_app


app = get_app()

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
