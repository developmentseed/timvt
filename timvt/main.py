"""TiMVT application."""

import pathlib

from timvt import __version__ as timvt_version
from timvt.db import close_db_connection, connect_to_db, register_table_catalog
from timvt.errors import DEFAULT_STATUS_CODES, add_exception_handlers
from timvt.factory import TMSFactory, VectorTilerFactory
from timvt.layer import Function, FunctionRegistry
from timvt.middleware import CacheControlMiddleware
from timvt.settings import ApiSettings, PostgresSettings

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
postgres_settings = PostgresSettings()

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


app.add_middleware(CacheControlMiddleware, cachecontrol=settings.cachecontrol)
app.add_middleware(CompressionMiddleware, minimum_size=0)
add_exception_handlers(app, DEFAULT_STATUS_CODES)

# We add the function registry to the application state
app.state.timvt_function_catalog = FunctionRegistry()
if settings.functions_directory:
    functions = pathlib.Path(settings.functions_directory).glob("*.sql")
    for func in functions:
        name = func.name
        if name.endswith(".sql"):
            name = name[:-4]
        app.state.timvt_function_catalog.register(
            Function.from_file(id=name, infile=str(func))
        )


# Register Start/Stop application event handler to setup/stop the database connection
@app.on_event("startup")
async def startup_event():
    """Application startup: register the database connection and create table list."""
    await connect_to_db(app, settings=postgres_settings)
    await register_table_catalog(
        app,
        schemas=postgres_settings.db_schemas,
        tables=postgres_settings.db_tables,
    )


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
    table_catalog = getattr(request.app.state, "table_catalog", {})
    return templates.TemplateResponse(
        name="index.html",
        context={"index": table_catalog.values(), "request": request},
        media_type="text/html",
    )


@app.get("/healthz", description="Health Check", tags=["Health Check"])
def ping():
    """Health check."""
    return {"ping": "pong!"}
