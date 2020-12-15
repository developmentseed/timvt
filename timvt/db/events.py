"""TiVTiler.db.events: database events."""

import logging

from buildpg import asyncpg

from timvt.settings import (
    DATABASE_URL,
    DB_MAX_CONN_SIZE,
    DB_MAX_INACTIVE_CONN_LIFETIME,
    DB_MAX_QUERIES,
    DB_MIN_CONN_SIZE,
)

from fastapi import FastAPI

logger = logging.getLogger(__name__)


async def connect_to_db(app: FastAPI) -> None:
    """Connect."""
    logger.info(f"Connecting to {DATABASE_URL}")
    app.state.pool = await asyncpg.create_pool_b(
        DATABASE_URL,
        min_size=DB_MIN_CONN_SIZE,
        max_size=DB_MAX_CONN_SIZE,
        max_queries=DB_MAX_QUERIES,
        max_inactive_connection_lifetime=DB_MAX_INACTIVE_CONN_LIFETIME,
    )
    logger.info("Connection established")


async def close_db_connection(app: FastAPI) -> None:
    """Close connection."""
    logger.info("Closing connection to database")
    await app.state.pool.close()
    logger.info("Connection closed")
