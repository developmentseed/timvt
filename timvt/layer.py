"""timvt Metadata models."""

import abc
from typing import Any, Dict, List, Optional

import morecantile
from buildpg import asyncpg
from pydantic import BaseModel, Field, root_validator

from timvt.settings import (
    DEFAULT_MAXZOOM,
    DEFAULT_MINZOOM,
    MAX_FEATURES_PER_TILE,
    TILE_BUFFER,
    TILE_RESOLUTION,
)


class Layer(BaseModel, metaclass=abc.ABCMeta):
    """Layer's Abstract BaseClass.

    Attributes:
        id (str): Layer's name.
        bounds (list): Layer's bounds (left, bottom, right, top).
        minzoom (int): Layer's min zoom level.
        maxzoom (int): Layer's max zoom level.
        tileurl (str, optional): Layer's tiles url.

    """

    id: str
    bounds: List[float] = [-180, -90, 180, 90]
    minzoom: int = DEFAULT_MINZOOM
    maxzoom: int = DEFAULT_MAXZOOM
    tileurl: Optional[str]

    @abc.abstractmethod
    async def get_tile(
        self,
        pool: asyncpg.BuildPgPool,
        tile: morecantile.Tile,
        tms: morecantile.TileMatrixSet,
        **kwargs: Any,
    ) -> bytes:
        """Return Tile Data.

        Args:
            pool (asyncpg.BuildPgPool): AsyncPG database connection pool.
            tile (morecantile.Tile): Tile object with X,Y,Z indices.
            tms (morecantile.TileMatrixSet): Tile Matrix Set.
            kwargs (any, optiona): Optional parameters to forward to the SQL function.

        Returns:
            bytes: Mapbox Vector Tiles.

        """
        ...


class Table(Layer):
    """Table Reader.

    Attributes:
        id (str): Layer's name.
        bounds (list): Layer's bounds (left, bottom, right, top).
        minzoom (int): Layer's min zoom level.
        maxzoom (int): Layer's max zoom level.
        tileurl (str, optional): Layer's tiles url.
        type (str): Layer's type.
        schema (str): Table's database schema (e.g public).
        geometry_type (str): Table's geometry type (e.g polygon).
        geometry_column (str): Name of the geomtry column in the table.
        properties (Dict): Properties available in the table.

    """

    type: str = "Table"
    dbschema: str = Field(..., alias="schema")
    table: str
    geometry_type: str
    geometry_column: str
    properties: Dict[str, str]

    async def get_tile(
        self,
        pool: asyncpg.BuildPgPool,
        tile: morecantile.Tile,
        tms: morecantile.TileMatrixSet,
        **kwargs: Any,
    ):
        """Get Tile Data."""
        bbox = tms.xy_bounds(tile)

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
                epsg=tms.crs.to_epsg(),
                seg_size=segSize,
                tile_resolution=int(resolution),
                tile_buffer=int(buffer),
            )


class Function(Layer):
    """Function Reader.

    Attributes:
        id (str): Layer's name.
        bounds (list): Layer's bounds (left, bottom, right, top).
        minzoom (int): Layer's min zoom level.
        maxzoom (int): Layer's max zoom level.
        tileurl (str, optional): Layer's tiles url.
        type (str): Layer's type.
        function_name (str): Nane of the SQL function to call. Defaults to `id`.
        sql (str): Valid SQL function which returns Tile data.
        options (list, optional): options available for the SQL function.

    """

    type: str = "Function"
    sql: str
    function_name: Optional[str]
    options: Optional[List[Dict[str, Any]]]

    @root_validator
    def function_name_default(cls, values):
        """Define default function's name to be same as id."""
        function_name = values.get("function_name")
        if function_name is None:
            values["function_name"] = values.get("id")
        return values

    @classmethod
    def from_file(cls, id: str, infile: str, **kwargs: Any):
        """load sql from file"""
        with open(infile) as f:
            sql = f.read()

        return cls(id=id, sql=sql, **kwargs)

    async def get_tile(
        self,
        pool: asyncpg.BuildPgPool,
        tile: morecantile.Tile,
        tms: morecantile.TileMatrixSet,
        **kwargs: Any,
    ):
        """Get Tile Data."""
        bbox = tms.xy_bounds(tile)

        async with pool.acquire() as conn:
            transaction = conn.transaction()
            await transaction.start()
            await conn.execute(self.sql)

            function_params = ":xmin, :ymin, :xmax, :ymax, :epsg"
            if kwargs:
                params = ", ".join([f"{k} => {v}" for k, v in kwargs.items()])
                function_params += f", {params}"

            content = await conn.fetchval_b(
                f"SELECT {self.function_name}({function_params})",
                xmin=bbox.left,
                ymin=bbox.bottom,
                xmax=bbox.right,
                ymax=bbox.top,
                epsg=tms.crs.to_epsg(),
            )

            await transaction.rollback()

        return content
