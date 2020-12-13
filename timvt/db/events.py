"""TiVTiler.db.events: database events."""

import logging

from sqlalchemy.ext.asyncio import create_async_engine

from timvt.settings import DATABASE_URL, DB_MAX_CONN_SIZE, DB_MAX_INACTIVE_CONN_LIFETIME

from fastapi import FastAPI

logger = logging.getLogger(__name__)


async def connect_to_db(app: FastAPI) -> None:
    """Connect."""
    logger.info(f"Connecting to {DATABASE_URL}")
    app.state.pool = create_async_engine(
        DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        pool_timeout=DB_MAX_INACTIVE_CONN_LIFETIME,
        pool_size=DB_MAX_CONN_SIZE,
    )
    logger.info("Connection established")


async def close_db_connection(app: FastAPI) -> None:
    """Close connection."""
    logger.info("Closing connection to database")
    await app.state.pool.dispose()
    logger.info("Connection closed")
