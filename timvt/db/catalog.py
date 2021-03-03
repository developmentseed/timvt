"""timvt.db.catalog: Table catalog."""

import json
from typing import Sequence

from buildpg.asyncpg import BuildPgPool

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
        ) as coldict,
        (
            SELECT
                ARRAY[
                    ST_XMin(extent.geom),
                    ST_YMin(extent.geom),
                    ST_XMax(extent.geom),
                    ST_YMax(extent.geom)
                ]
            FROM (
                SELECT
                    coalesce(
                        ST_Transform(ST_SetSRID(ST_EstimatedExtent(f_table_schema, f_table_name, f_geometry_column), srid), 4326),
                        ST_MakeEnvelope(-180, -90, 180, 90, 4326)
                    ) as geom
            ) AS extent
        ) AS bounds
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
                'properties', coldict,
                'bounds', bounds
            )
        )
    FROM t
    ;
"""


async def table_index(db_pool: BuildPgPool) -> Sequence:
    """Fetch Table index."""
    async with db_pool.acquire() as conn:
        q = await conn.prepare(sql_query)
        content = await q.fetchval()
    return json.loads(content)
