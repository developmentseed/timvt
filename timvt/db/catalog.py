"""TiVTiler.db.catalog: Table catalog."""

import json
from typing import Mapping

from asyncpg.pool import Pool

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
                'schema', f_table_schema,
                'table', f_table_name,
                'geometry_column', f_geometry_column,
                'columns', coldict
            )
        )
    FROM t
    ;
"""


async def table_index(db_pool: Pool) -> Mapping:
    """Fetch Table index."""
    async with db_pool.acquire() as conn:
        q = await conn.prepare(sql_query)
        content = await q.fetchval()

    return json.loads(content)
