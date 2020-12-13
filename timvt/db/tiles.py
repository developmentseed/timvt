"""TiVTiler.db.tiles: tile reading"""

from dataclasses import dataclass, field
from typing import Dict

import morecantile
from asyncpg.pool import Pool
from morecantile import BoundingBox, TileMatrixSet

from timvt.db.functions import Function
from timvt.models.metadata import TableMetadata
from timvt.settings import MAX_FEATURES_PER_TILE, TILE_BUFFER, TILE_RESOLUTION

WEB_MERCATOR_TMS = morecantile.tms.get("WebMercatorQuad")


@dataclass
class VectorTileReader:
    """VectorTileReader"""

    db_pool: Pool
    tms: TileMatrixSet = field(default_factory=lambda: WEB_MERCATOR_TMS)

    async def _tile_from_bbox(
        self, bbox: BoundingBox, columns: str, table: TableMetadata
    ) -> bytes:
        """return a vector tile (bytes) for the input bounds"""
        epsg = self.tms.crs.to_epsg()
        segSize = bbox.right - bbox.left

        geometry_column = table.geometry_column
        cols = table.properties
        if geometry_column in cols:
            del cols[geometry_column]

        if columns is not None:
            include_cols = [c.strip() for c in columns.split(",")]
            for c in cols.copy():
                if c not in include_cols:
                    del cols[c]

        colstring = ", ".join(list(cols))

        limitval = str(int(MAX_FEATURES_PER_TILE))
        limit = f"LIMIT {limitval}" if MAX_FEATURES_PER_TILE > -1 else ""

        sql_query = f"""
            WITH
            bounds AS (
                SELECT
                    ST_Segmentize(
                        ST_MakeEnvelope(
                            $1,
                            $2,
                            $3,
                            $4,
                            $5
                        ),
                        $6
                    ) AS geom
            ),
            mvtgeom AS (
                SELECT ST_AsMVTGeom(
                    ST_Transform(t.{geometry_column}, $5),
                    bounds.geom,
                    $7,
                    $8
                ) AS geom, {colstring}
                FROM {table.id} t, bounds
                WHERE ST_Intersects(
                    ST_Transform(t.geom, 4326), ST_Transform(bounds.geom, 4326)
                ) {limit}
            )
            SELECT ST_AsMVT(mvtgeom.*) FROM mvtgeom
        """

        async with self.db_pool.acquire() as conn:
            q = await conn.prepare(sql_query)
            content = await q.fetchval(
                bbox.left,  # 1
                bbox.bottom,  # 2
                bbox.right,  # 3
                bbox.top,  # 4
                epsg,  # 5
                segSize,  # 6
                TILE_RESOLUTION,  # 7
                TILE_BUFFER,  # 8
            )

        return bytes(content)

    async def _tile_from_function(
        self, bbox: BoundingBox, function: Function, query_params
    ) -> bytes:
        pass

    async def tile(
        self, tile_x: int, tile_y: int, tile_z: int, columns: str, table: TableMetadata
    ) -> bytes:
        """read vector tile"""
        tile = morecantile.Tile(tile_x, tile_y, tile_z)
        bbox = self.tms.xy_bounds(tile)
        return await self._tile_from_bbox(bbox, columns, table)

    async def function(
        self,
        tile_x: int,
        tile_y: int,
        tile_z: int,
        function: Function,
        query_params: Dict,
    ) -> bytes:
        """read vector tile with custom function"""
        tile = morecantile.Tile(tile_x, tile_y, tile_z)
        bbox = self.tms.xy_bounds(tile)
        return await function(bbox, **query_params)
