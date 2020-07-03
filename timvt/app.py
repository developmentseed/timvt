"""TiVTiler app."""

import logging

from . import settings, version
from .endpoints import demo, health, index, tiles, tms
from .events import create_start_app_handler, create_stop_app_handler

from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

logger = logging.getLogger(__name__)

# Create TiVTiler Application.
app = FastAPI(
    title=settings.APP_NAME,
    description="A lightweight PostGIS vector tile server.",
    version=version,
)
app.debug = settings.DEBUG

# Setup CORS.
if settings.CORS_ORIGINS:
    origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

# Add GZIP compression by default.
app.add_middleware(GZipMiddleware, minimum_size=0)

# Register Start/Stop application event handler to setup/stop the database connection
app.add_event_handler("startup", create_start_app_handler(app))
app.add_event_handler("shutdown", create_stop_app_handler(app))

# Register endpoints.
app.include_router(health.router)
app.include_router(tiles.router)
app.include_router(tms.router)
app.include_router(demo.router)
app.include_router(index.router)
