"""TiVTiler.db.events: database events."""

import asyncpg
from fastapi import FastAPI
import logging

from ..settings import (
    DATABASE_URL,
    DB_MIN_CONN_SIZE,
    DB_MAX_CONN_SIZE,
    DB_MAX_QUERIES,
    DB_MAX_INACTIVE_CONN_LIFETIME,
)


logger = logging.getLogger(__name__)


async def connect_to_db(app: FastAPI) -> None:
    logger.info(f"Connecting to {DATABASE_URL}")
    min_size = DB_MIN_CONN_SIZE
    max_size = DB_MAX_CONN_SIZE
    max_queries = DB_MAX_QUERIES
    max_conn_lifetime = DB_MAX_INACTIVE_CONN_LIFETIME

    app.state.pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=min_size,
        max_size=max_size,
        max_queries=max_queries,
        max_inactive_connection_lifetime=max_conn_lifetime
    )
    logger.info("Connection established")


async def close_db_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")
    await app.state.pool.close()
    logger.info("Connection closed")