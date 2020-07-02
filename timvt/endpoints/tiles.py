"""TiVTiler.endpoints.tiles: Vector Tiles endpoint."""

from typing import Any, Dict

from asyncpg.pool import Pool

from ..ressources.enums import MimeTypes
from ..ressources.responses import TileResponse
from ..settings import MAX_FEATURES_PER_TILE, TILE_BUFFER, TILE_RESOLUTION
from ..utils.dependencies import TileParams, _get_db_pool
from ..utils.timings import Timer

from fastapi import APIRouter, Depends, Path, Request
from fastapi.responses import JSONResponse

router = APIRouter()

params: Dict[str, Any] = {
    "responses": {200: {"content": {"application/x-protobuf": {}}}},
    "response_class": TileResponse,
    "tags": ["Tiles"],
}


@router.get("/tiles/{table}/{z}/{x}/{y}.pbf", name="tile_3857", **params)
@router.get("/tiles/{identifier}/{table}/{z}/{x}/{y}.pbf", **params)
async def tile(
    request: Request,
    table: str = Path(..., description="Table Name"),
    tile_params: TileParams = Depends(),
    db_pool: Pool = Depends(_get_db_pool),
    columns: str = None,
) -> TileResponse:
    """Handle /tiles requests."""
    table_idx = request.app.state.Catalog.get_table(table)
    if table_idx is None:
        error = {"error": "Table not found"}
        return JSONResponse(content=error, status_code=404)
    geometry_column = table_idx["geometry_column"]

    timings = []
    headers: Dict[str, str] = {}

    bbox = tile_params.tms.xy_bounds(tile_params.tile)
    epsg = tile_params.tms.crs.to_epsg()
    segSize = (bbox.xmax - bbox.xmin) / 4

    cols = table_idx["columns"]
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
            FROM {table} t, bounds
            WHERE ST_Intersects(
                ST_Transform(t.geom, 4326), ST_Transform(bounds.geom, 4326)
            ) {limit}
        )
        SELECT ST_AsMVT(mvtgeom.*) FROM mvtgeom
    """

    with Timer() as t:
        async with db_pool.acquire() as conn:
            q = await conn.prepare(sql_query)
            content = await q.fetchval(
                bbox.xmin,  # 1
                bbox.ymin,  # 2
                bbox.xmax,  # 3
                bbox.ymax,  # 4
                epsg,  # 5
                segSize,  # 6
                TILE_RESOLUTION,  # 7
                TILE_BUFFER,  # 8
            )
    timings.append(("db-read", t.elapsed))

    if timings:
        headers["X-Server-Timings"] = "; ".join(
            ["{} - {:0.2f}".format(name, time * 1000) for (name, time) in timings]
        )

    return TileResponse(bytes(content), media_type=MimeTypes.pbf.value, headers=headers)
