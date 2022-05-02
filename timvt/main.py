"""TiVTiler app."""

from timvt import __version__ as timvt_version
from timvt.db import close_db_connection, connect_to_db, register_table_catalog
from timvt.factory import TMSFactory, VectorTilerFactory
from timvt.layer import FunctionRegistry
from timvt.settings import ApiSettings

from fastapi import FastAPI, Request

from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from starlette_cramjam.middleware import CompressionMiddleware

try:
    from importlib.resources import files as resources_files  # type: ignore
except ImportError:
    from importlib_resources import files as resources_files  # type: ignore


templates = Jinja2Templates(directory=str(resources_files(__package__) / "templates"))  # type: ignore
settings = ApiSettings()

# Create TiVTiler Application.
app = FastAPI(
    title=settings.name,
    description="A lightweight PostGIS vector tile server.",
    version=timvt_version,
    debug=settings.debug,
)

# Setup CORS.
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

app.add_middleware(CompressionMiddleware, minimum_size=0)

# We add the function registry to the application state
app.state.function_catalog = FunctionRegistry()


# Register Start/Stop application event handler to setup/stop the database connection
@app.on_event("startup")
async def startup_event():
    """Application startup: register the database connection and create table list."""
    await connect_to_db(app)
    await register_table_catalog(app)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown: de-register the database connection."""
    await close_db_connection(app)


# Register endpoints.
mvt_tiler = VectorTilerFactory(
    with_tables_metadata=True,
    with_functions_metadata=True,
    with_viewer=True,
)
app.include_router(mvt_tiler.router)

tms = TMSFactory()
app.include_router(tms.router, tags=["TileMatrixSets"])


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    """DEMO."""
    return templates.TemplateResponse(
        name="index.html",
        context={"index": request.app.state.table_catalog, "request": request},
        media_type="text/html",
    )


@app.get("/healthz", description="Health Check", tags=["Health Check"])
def ping():
    """Health check."""
    return {"ping": "pong!"}
