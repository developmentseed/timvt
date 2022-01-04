"""timvt Metadata models."""

import abc
import json
from typing import Any, Dict, List, Optional

import morecantile
from buildpg import Func
from buildpg import Var as pg_variable
from buildpg import asyncpg, clauses, funcs, render, select_fields
from pydantic import BaseModel, Field, root_validator

from timvt.errors import MissingEPSGCode
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
        srid (int): Table's SRID
        geometry_column (str): Name of the geomtry column in the table.
        properties (Dict): Properties available in the table.

    """

    type: str = "Table"
    dbschema: str = Field(..., alias="schema")
    table: str
    geometry_type: str
    geometry_column: str
    geometry_srid: int
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
        limit = min(int(limit), MAX_FEATURES_PER_TILE)
        if limit == -1:
            limit = MAX_FEATURES_PER_TILE

        columns = kwargs.get(
            "columns"
        )  # Comma-seprated list of properties (column's name) to include in the tile
        resolution = kwargs.get("resolution", str(TILE_RESOLUTION))  # Tile's resolution
        buffer = kwargs.get(
            "buffer", str(TILE_BUFFER)
        )  # Size of extra data to add for a tile.

        # create list of columns to return
        geometry_column = self.geometry_column
        geometry_srid = self.geometry_srid
        cols = self.properties
        if geometry_column in cols:
            del cols[geometry_column]

        if columns is not None:
            include_cols = [c.strip() for c in columns.split(",")]
            for c in cols.copy():
                if c not in include_cols:
                    del cols[c]

        segSize = bbox.right - bbox.left

        tms_srid = tms.crs.to_epsg()
        tms_proj = tms.crs.to_proj4()

        async with pool.acquire() as conn:
            sql_query = """
                WITH
                -- bounds (the tile envelope) in TMS's CRS (SRID)
                bounds_tmscrs AS (
                    SELECT
                        ST_Segmentize(
                            ST_MakeEnvelope(
                                :xmin,
                                :ymin,
                                :xmax,
                                :ymax,
                                -- If EPSG is null we set it to 0
                                coalesce(:tms_srid, 0)
                            ),
                            :seg_size
                        ) AS geom
                ),
                bounds_geomcrs AS (
                    SELECT
                        CASE WHEN coalesce(:tms_srid, 0) != 0 THEN
                            ST_Transform(bounds_tmscrs.geom, :geometry_srid)
                        ELSE
                            ST_Transform(bounds_tmscrs.geom, :tms_proj, :geometry_srid)
                        END as geom
                    FROM bounds_tmscrs
                ),
                mvtgeom AS (
                    SELECT ST_AsMVTGeom(
                        CASE WHEN :tms_srid IS NOT NULL THEN
                            ST_Transform(t.:geometry_column, :tms_srid)
                        ELSE
                            ST_Transform(t.:geometry_column, :tms_proj)
                        END,
                        bounds_tmscrs.geom,
                        :tile_resolution,
                        :tile_buffer
                    ) AS geom, :fields
                    FROM :tablename t, bounds_tmscrs, bounds_geomcrs
                    -- Find where geometries intersect with input Tile
                    -- Intersects test is made in table geometry's CRS (e.g WGS84)
                    WHERE ST_Intersects(
                        t.:geometry_column, bounds_geomcrs.geom
                    ) LIMIT :limit
                )
                SELECT ST_AsMVT(mvtgeom.*) FROM mvtgeom
            """

            q, p = render(
                sql_query,
                tablename=pg_variable(self.id),
                geometry_column=pg_variable(geometry_column),
                fields=select_fields(*cols),
                xmin=bbox.left,
                ymin=bbox.bottom,
                xmax=bbox.right,
                ymax=bbox.top,
                geometry_srid=funcs.cast(geometry_srid, "int"),
                tms_proj=tms_proj,
                tms_srid=tms_srid,
                seg_size=segSize,
                tile_resolution=int(resolution),
                tile_buffer=int(buffer),
                limit=limit,
            )

            return await conn.fetchval(q, *p)


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
        # We only support TMS with valid EPSG code
        if not tms.crs.to_epsg():
            raise MissingEPSGCode(
                f"{tms.identifier}'s CRS does not have a valid EPSG code."
            )

        bbox = tms.xy_bounds(tile)

        async with pool.acquire() as conn:
            transaction = conn.transaction()
            await transaction.start()
            # Register the custom function
            await conn.execute(self.sql)

            # Build the query
            sql_query = clauses.Select(
                Func(
                    self.function_name,
                    ":xmin",
                    ":ymin",
                    ":xmax",
                    ":ymax",
                    ":epsg",
                    ":query_params",
                ),
            )
            q, p = render(
                str(sql_query),
                xmin=bbox.left,
                ymin=bbox.bottom,
                xmax=bbox.right,
                ymax=bbox.top,
                epsg=tms.crs.to_epsg(),
                query_params=json.dumps(kwargs),
            )

            # execute the query
            content = await conn.fetchval(q, *p)

            # rollback
            await transaction.rollback()

        return content
