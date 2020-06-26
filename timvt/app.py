"""TiVTiler app."""
import logging
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from . import version
from . import settings
from .endpoints import tiles, health
from .events import create_start_app_handler, create_stop_app_handler

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="A lightweight Vector Tile server",
    version=version,
)
app.debug = settings.DEBUG
if settings.CORS_ORIGINS:
    origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

app.add_middleware(GZipMiddleware, minimum_size=0)
app.add_event_handler("startup", create_start_app_handler(app))
app.add_event_handler("shutdown", create_stop_app_handler(app))

app.include_router(health.router)
app.include_router(tiles.router)
