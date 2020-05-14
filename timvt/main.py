"""titiler app."""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from timvt.core import config
from timvt.api.api_v1.api import router


app = FastAPI(
    title=config.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json",
    description="A lightweight MVT tile server",
    version="0.0.1",
)

if config.BACKEND_CORS_ORIGINS:
    origins = [origin.strip() for origin in config.BACKEND_CORS_ORIGINS.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

app.add_middleware(GZipMiddleware, minimum_size=0)

app.include_router(router, prefix=config.API_VERSION_STR)
