"""TiVTiler.db.catalog: Table catalog."""

from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.sql import text

sql_query = """
    WITH geo_tables AS (
        SELECT
            f_table_schema,
            f_table_name,
            f_geometry_column,
            type,
            srid
        FROM
            geometry_columns
    ), t AS (
    SELECT
        f_table_schema,
        f_table_name,
        f_geometry_column,
        type,
        srid,
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
        f_geometry_column,
        type,
        srid
    )
    SELECT
        jsonb_agg(
            jsonb_build_object(
                'id', concat(f_table_schema, '.', f_table_name),
                'schema', f_table_schema,
                'table', f_table_name,
                'geometry_column', f_geometry_column,
                'srid', srid,
                'geometry_type', type,
                'properties', coldict
            )
        )
    FROM t
    ;
"""


async def table_index(db_pool: AsyncEngine) -> Sequence:
    """Fetch Table index."""
    async with db_pool.begin() as conn:
        q = await conn.execute(text(sql_query))
        content = q.first()[0]
    return content
