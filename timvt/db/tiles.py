"""timvt.db.tiles: tile reading"""

from dataclasses import dataclass, field

import morecantile
from buildpg.asyncpg import BuildPgPool
from morecantile import BoundingBox, TileMatrixSet

from timvt.models.metadata import TableMetadata
from timvt.settings import MAX_FEATURES_PER_TILE, TILE_BUFFER, TILE_RESOLUTION

WEB_MERCATOR_TMS = morecantile.tms.get("WebMercatorQuad")


@dataclass
class VectorTileReader:
    """VectorTileReader"""

    db_pool: BuildPgPool
    table: TableMetadata
    tms: TileMatrixSet = field(default_factory=lambda: WEB_MERCATOR_TMS)

    async def _tile_from_bbox(self, bbox: BoundingBox, columns: str) -> bytes:
        """return a vector tile (bytes) for the input bounds"""
        epsg = self.tms.crs.to_epsg()
        segSize = bbox.right - bbox.left

        geometry_column = self.table.geometry_column
        cols = self.table.properties
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
                FROM {self.table.id} t, bounds
                WHERE ST_Intersects(
                    ST_Transform(t.geom, 4326), ST_Transform(bounds.geom, 4326)
                ) {limit}
            )
            SELECT ST_AsMVT(mvtgeom.*) FROM mvtgeom
        """

        async with self.db_pool.acquire() as conn:
            content = await conn.fetchval_b(
                sql_query,
                xmin=bbox.left,
                ymin=bbox.bottom,
                xmax=bbox.right,
                ymax=bbox.top,
                epsg=epsg,
                seg_size=segSize,
                tile_resolution=TILE_RESOLUTION,
                tile_buffer=TILE_BUFFER,
            )

        return bytes(content)

    async def tile(self, tile_x: int, tile_y: int, tile_z: int, columns: str) -> bytes:
        """read vector tile"""
        tile = morecantile.Tile(tile_x, tile_y, tile_z)
        bbox = self.tms.xy_bounds(tile)
        return await self._tile_from_bbox(bbox, columns)
