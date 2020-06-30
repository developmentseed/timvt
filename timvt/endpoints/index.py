"""TiVTiler.index: Index endpoint."""

import json
from typing import Dict

import asyncstdlib
from asyncpg.pool import Pool

from ..ressources.enums import MimeTypes
from ..ressources.responses import TileResponse
from ..utils.dependencies import _get_db_pool

from fastapi import APIRouter, Depends

router = APIRouter()


@asyncstdlib.lru_cache()
async def index(db_pool: Pool) -> Dict:
    """Get list of available layers."""
    sql_query = """
        WITH geo_tables AS (
            SELECT
                f_table_schema,
                f_table_name,
                f_geometry_column
            FROM
                geometry_columns
        ), t AS (
        SELECT
            f_table_schema,
            f_table_name,
            f_geometry_column,
            jsonb_object(
                array_agg(column_name),
                array_agg(udt_name)
            ) as coldict
        FROM
            information_schema.columns,
            geo_tables
        WHERE
            f_table_schema=table_schema
            AND
            f_table_name=table_name
        GROUP BY
            f_table_schema,
            f_table_name,
            f_geometry_column
        )
        SELECT
            jsonb_agg(
                jsonb_build_object(
                    f_table_name,
                    jsonb_build_object(
                        'schema', f_table_schema,
                        'table', f_table_name,
                        'geometry_column', f_geometry_column,
                        'columns', coldict
                    )
                )
            )
        FROM t
        ;
    """

    async with db_pool.acquire() as conn:
        q = await conn.prepare(sql_query)
        content = await q.fetchval()

    j = json.loads(content)
    assoc = {}
    for rec in j:
        for k, v in rec.items():
            assoc[k] = v

    return assoc


@router.get("/index")
async def display_index(db_pool: Pool = Depends(_get_db_pool),) -> TileResponse:
    """Display table index."""
    assoc = await index(db_pool)
    return TileResponse(
        bytes(json.dumps(assoc), encoding="utf8"), media_type=MimeTypes.json.value,
    )
