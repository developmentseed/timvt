"""timvt Metadata models."""

import abc
from typing import Any, Dict, List, Optional

from buildpg import asyncpg
from morecantile import BoundingBox
from pydantic import BaseModel, Field

from timvt.settings import (
    DEFAULT_MAXZOOM,
    DEFAULT_MINZOOM,
    MAX_FEATURES_PER_TILE,
    TILE_BUFFER,
    TILE_RESOLUTION,
)


class Layer(BaseModel, metaclass=abc.ABCMeta):
    """Layer BaseClass."""

    id: str
    bounds: List[float] = [-180, -90, 180, 90]
    minzoom: int = DEFAULT_MINZOOM
    maxzoom: int = DEFAULT_MAXZOOM
    tileurl: Optional[str]

    @abc.abstractmethod
    async def get_tile(
        self, pool: asyncpg.BuildPgPool, bbox: BoundingBox, epsg: int, **kwargs: Any,
    ) -> bytes:
        """Return Tile Data."""
        ...


class Table(Layer):
    """Table Reader."""

    type: str = "Table"
    dbschema: str = Field(..., alias="schema")
    table: str
    geometry_type: str
    geometry_column: str
    properties: Dict[str, str]

    async def get_tile(
        self, pool: asyncpg.BuildPgPool, bbox: BoundingBox, epsg: int, **kwargs: Any,
    ):
        """Get Tile Data."""
        limit = kwargs.get(
            "limit", str(MAX_FEATURES_PER_TILE)
        )  # Number of features to write to a tile.
        columns = kwargs.get(
            "columns"
        )  # Comma-seprated list of properties (column's name) to include in the tile
        resolution = kwargs.get("resolution", str(TILE_RESOLUTION))  # Tile's resolution
        buffer = kwargs.get(
            "buffer", str(TILE_BUFFER)
        )  # Size of extra data to add for a tile.

        limitstr = f"LIMIT {limit}" if int(limit) > -1 else ""

        # create list of columns to return
        geometry_column = self.geometry_column
        cols = self.properties
        if geometry_column in cols:
            del cols[geometry_column]

        if columns is not None:
            include_cols = [c.strip() for c in columns.split(",")]
            for c in cols.copy():
                if c not in include_cols:
                    del cols[c]
        colstring = ", ".join(list(cols))

        segSize = bbox.right - bbox.left

        async with pool.acquire() as conn:
            sql_query = f"""
                WITH
                bounds AS (
                    SELECT
                        ST_Segmentize(
                            ST_MakeEnvelope(
                                :xmin,
                                :ymin,
                                :xmax,
                                :ymax,
                                :epsg
                            ),
                            :seg_size
                        ) AS geom
                ),
                mvtgeom AS (
                    SELECT ST_AsMVTGeom(
                        ST_Transform(t.{geometry_column}, :epsg),
                        bounds.geom,
                        :tile_resolution,
                        :tile_buffer
                    ) AS geom, {colstring}
                    FROM {self.id} t, bounds
                    WHERE ST_Intersects(
                        ST_Transform(t.{geometry_column}, 4326),
                        ST_Transform(bounds.geom, 4326)
                    ) {limitstr}
                )
                SELECT ST_AsMVT(mvtgeom.*) FROM mvtgeom
            """
            return await conn.fetchval_b(
                sql_query,
                xmin=bbox.left,
                ymin=bbox.bottom,
                xmax=bbox.right,
                ymax=bbox.top,
                epsg=epsg,
                seg_size=segSize,
                tile_resolution=int(resolution),
                tile_buffer=int(buffer),
            )


class Function(Layer):
    """Function Reader."""

    type: str = "Function"
    sql: str

    @classmethod
    def from_file(cls, id: str, infile: str):
        """load sql from file"""
        with open(infile) as f:
            sql = f.read()

        return cls(id=id, sql=sql)

    async def get_tile(
        self, pool: asyncpg.BuildPgPool, bbox: BoundingBox, epsg: int, **kwargs: Any,
    ):
        """Get Tile Data."""
        async with pool.acquire() as conn:
            transaction = conn.transaction()
            await transaction.start()
            await conn.execute(self.sql)

            function_params = ":xmin, :ymin, :xmax, :ymax, :epsg"
            if kwargs:
                params = ", ".join([f"{k} => {v}" for k, v in kwargs.items()])
                function_params += f", {params}"

            content = await conn.fetchval_b(
                f"SELECT {self.id}({function_params})",
                xmin=bbox.left,
                ymin=bbox.bottom,
                xmax=bbox.right,
                ymax=bbox.top,
                epsg=epsg,
            )

            await transaction.rollback()

        return content
