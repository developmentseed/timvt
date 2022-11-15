"""
TiMVT config.

TiMVT uses pydantic.BaseSettings to either get settings from `.env` or environment variables
see: https://pydantic-docs.helpmanual.io/usage/settings/

"""
import sys
from functools import lru_cache
from typing import Any, Dict, List, Optional

import pydantic

# Pydantic does not support older versions of typing.TypedDict
# https://github.com/pydantic/pydantic/pull/3374
if sys.version_info < (3, 9, 2):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict


class TableConfig(TypedDict, total=False):
    """Configuration to add table options with env variables."""

    geomcol: Optional[str]
    datetimecol: Optional[str]
    pk: Optional[str]
    properties: Optional[List[str]]


class TableSettings(pydantic.BaseSettings):
    """Table configuration settings"""

    fallback_key_names: List[str] = ["ogc_fid", "id", "pkey", "gid"]
    table_config: Dict[str, TableConfig] = {}

    class Config:
        """model config"""

        env_prefix = "TIMVT_"
        env_file = ".env"
        env_nested_delimiter = "__"


class _ApiSettings(pydantic.BaseSettings):
    """API settings"""

    name: str = "TiMVT"
    cors_origins: str = "*"
    cachecontrol: str = "public, max-age=3600"
    debug: bool = False
    functions_directory: Optional[str]

    @pydantic.validator("cors_origins")
    def parse_cors_origin(cls, v):
        """Parse CORS origins."""
        return [origin.strip() for origin in v.split(",")]

    class Config:
        """model config"""

        env_prefix = "TIMVT_"
        env_file = ".env"


@lru_cache()
def ApiSettings() -> _ApiSettings:
    """
    This function returns a cached instance of the APISettings object.
    Caching is used to prevent re-reading the environment every time the API settings are used in an endpoint.
    If you want to change an environment variable and reset the cache (e.g., during testing), this can be done
    using the `lru_cache` instance method `get_api_settings.cache_clear()`.

    From https://github.com/dmontagu/fastapi-utils/blob/af95ff4a8195caaa9edaa3dbd5b6eeb09691d9c7/fastapi_utils/api_settings.py#L60-L69
    """
    return _ApiSettings()


class _TileSettings(pydantic.BaseSettings):
    """MVT settings"""

    tile_resolution: int = 4096
    tile_buffer: int = 256
    max_features_per_tile: int = 10000
    default_tms: str = "WebMercatorQuad"
    default_minzoom: int = 0
    default_maxzoom: int = 22

    class Config:
        """model config"""

        env_prefix = "TIMVT_"
        env_file = ".env"


@lru_cache()
def TileSettings() -> _TileSettings:
    """Cache settings."""
    return _TileSettings()


class PostgresSettings(pydantic.BaseSettings):
    """Postgres-specific API settings.

    Attributes:
        postgres_user: postgres username.
        postgres_pass: postgres password.
        postgres_host: hostname for the connection.
        postgres_port: database port.
        postgres_dbname: database name.
    """

    postgres_user: Optional[str]
    postgres_pass: Optional[str]
    postgres_host: Optional[str]
    postgres_port: Optional[str]
    postgres_dbname: Optional[str]

    database_url: Optional[pydantic.PostgresDsn] = None

    db_min_conn_size: int = 1
    db_max_conn_size: int = 10
    db_max_queries: int = 50000
    db_max_inactive_conn_lifetime: float = 300

    db_schemas: List[str] = ["public"]
    db_tables: Optional[List[str]]

    class Config:
        """model config"""

        env_file = ".env"

    # https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/core/config.py#L42
    @pydantic.validator("database_url", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Validate database config."""
        if isinstance(v, str):
            return v

        return pydantic.PostgresDsn.build(
            scheme="postgresql",
            user=values.get("postgres_user"),
            password=values.get("postgres_pass"),
            host=values.get("postgres_host", ""),
            port=values.get("postgres_port", 5432),
            path=f"/{values.get('postgres_dbname') or ''}",
        )
