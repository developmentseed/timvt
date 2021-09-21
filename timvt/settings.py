"""
TiMVT config.

TiVTiler uses starlette.config to either get settings from `.env` or environment variables
see: https://www.starlette.io/config/

"""

from starlette.config import Config

config = Config(".env")

# API config
APP_NAME = config("APP_NAME", cast=str, default="TiMVT")
DEBUG = config("DEBUG", cast=bool, default=False)
CORS_ORIGINS = config("CORS_ORIGINS", cast=str, default="*")

# Database config
DATABASE_URL = config("DATABASE_URL", cast=str, default="")
if not DATABASE_URL:
    POSTGRES_USER = config("POSTGRES_USER", cast=str)
    POSTGRES_PASS = config("POSTGRES_PASS", cast=str)
    POSTGRES_DBNAME = config("POSTGRES_DBNAME", cast=str)
    POSTGRES_PORT = config("POSTGRES_PORT", cast=str)
    POSTGRES_HOST = config("POSTGRES_HOST", cast=str)

    DATABASE_URL = (
        f"postgresql://{POSTGRES_USER}:"
        f"{POSTGRES_PASS}@{POSTGRES_HOST}:"
        f"{POSTGRES_PORT}/{POSTGRES_DBNAME}"
    )

DB_MIN_CONN_SIZE = config("DB_MIN_CONN_SIZE", cast=int, default=1)
DB_MAX_CONN_SIZE = config("DB_MAX_CONN_SIZE", cast=int, default=10)
DB_MAX_QUERIES = config("DB_MAX_QUERIES", cast=int, default=50000)
DB_MAX_INACTIVE_CONN_LIFETIME = config(
    "DB_MAX_INACTIVE_CONN_LIFETIME", cast=float, default=300.0
)

# Tile / Table config
TILE_RESOLUTION = config("TILE_RESOLUTION", cast=int, default=4096)
TILE_BUFFER = config("TILE_BUFFER", cast=int, default=256)
MAX_FEATURES_PER_TILE = config("MAX_FEATURES_PER_TILE", cast=int, default=10000)
DEFAULT_MINZOOM = config("DEFAULT_MINZOOM", cast=int, default=0)
DEFAULT_MAXZOOM = config("DEFAULT_MAXZOOM", cast=int, default=22)
