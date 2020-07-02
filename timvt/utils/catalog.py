"""TiVTiler.utils.dependencies: endpoint's dependencies."""

from enum import Enum
import json

from fastapi import FastAPI


class Catalog:
    def __init__(self, app: FastAPI):
        self.app = app

    async def init(self):
        self.index = await self.get_index()
        self.Tables = self.get_tables_enum()

    @property
    def sql(self):
        return """
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

    async def get_index(self):
        async with self.app.state.pool.acquire() as conn:
            q = await conn.prepare(self.sql)
            content = await q.fetchval()
        self.index = json.loads(content)
        return self.index

    def get_table(self, table: str):
        schema = None
        split = table.split(".")
        if len(split) == 2:
            schema = split[0]
            table = split[1]
        for r in self.index:
            if r["table"] == table:
                if schema is None or r["schema"] == schema:
                    return r
        return None

    def get_tables_enum(self):
        table_list = [r["table"] for r in self.index]
        Tables = Enum("Tables", [(a, a) for a in table_list])
        return Tables
