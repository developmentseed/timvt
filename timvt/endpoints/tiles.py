"""TiVTiler.endpoints.tiles: Vector Tiles endpoint."""

import re
from typing import Any, Dict

from asyncpg.pool import Pool

from ..ressources.enums import MimeTypes
from ..ressources.responses import TileResponse
from ..utils.dependencies import TileParams, _get_db_pool
from ..utils.timings import Timer

from fastapi import APIRouter, Depends, Path

router = APIRouter()

params: Dict[str, Any] = {
    "responses": {200: {"content": {"application/x-protobuf": {}}}},
    "response_class": TileResponse,
    "tags": ["Tiles"],
}


@router.get("/tiles/{table}/{z}/{x}/{y}\\.pbf", **params)
@router.get("/tiles/{identifier}/{table}/{z}/{x}/{y}\\.pbf", **params)
async def tile(
    table: str = Path(..., description="Table Name"),
    tile_params: TileParams = Depends(),
    db_pool: Pool = Depends(_get_db_pool),
) -> TileResponse:
    """Handle /tiles requests."""
    timings = []
    headers: Dict[str, str] = {}

    with Timer() as t:
        tms = tile_params.tms
        tile = tile_params.tile

        bbox = tms.xy_bounds(tile)
        epsg = tms.crs.to_epsg()

    timings.append(("tms-ops", t.elapsed))

    segSize = (bbox.xmax - bbox.xmin) / 4
    if not re.match(r"^[a-z]+[a-z_\-0-9]*$", table, re.I):
        raise Exception("Bad tablename")

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
            SELECT ST_AsMVTGeom(ST_Transform(t.geom, $5), bounds.geom) AS geom, *
            FROM "{table}" t, bounds
            WHERE ST_Intersects(
                ST_Transform(t.geom, 4326),
                ST_Transform(bounds.geom, 4326)
            )
        )
        SELECT ST_AsMVT(mvtgeom.*) FROM mvtgeom
    """
    with Timer() as t:
        async with db_pool.acquire() as conn:
            q = await conn.prepare(sql_query)
            content = await q.fetchval(
                bbox.xmin, bbox.ymin, bbox.xmax, bbox.ymax, epsg, segSize
            )
    timings.append(("db-read", t.elapsed))

    if timings:
        headers["X-Server-Timings"] = "; ".join(
            ["{} - {:0.2f}".format(name, time * 1000) for (name, time) in timings]
        )

    return TileResponse(bytes(content), media_type=MimeTypes.pbf.value, headers=headers)
