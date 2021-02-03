"""TiVTiler app."""

import logging

from timvt import __version__ as timvt_version
from timvt import settings
from timvt.db.catalog import table_index
from timvt.db.events import close_db_connection, connect_to_db
from timvt.endpoints import demo, health, tiles, tms
from timvt.resources.responses import JSONIndented

from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

logger = logging.getLogger(__name__)

# Create TiVTiler Application.
app = FastAPI(
    title=settings.APP_NAME,
    description="A lightweight PostGIS vector tile server.",
    version=timvt_version,
    default_response_class=JSONIndented,
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
@app.on_event("startup")
async def startup_event():
    """Application startup: register the database connection and create table list."""
    await connect_to_db(app)
    # Fetch database table list
    app.state.Catalog = await table_index(app.state.pool)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown: de-register the database connection."""
    await close_db_connection(app)


# Register endpoints.
app.include_router(tiles.router, tags=["Tiles"])
app.include_router(tms.router, tags=["TileMatrixSets"])
app.include_router(demo.router, tags=["demo"])
app.include_router(health.router, tags=["Health Check"])
