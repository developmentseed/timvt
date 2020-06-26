"""timvt api."""

from typing import Any, Dict

from fastapi import APIRouter
from fastapi import Path, Query
from fastapi.responses import HTMLResponse

import morecantile

from timvt.ressources.common import mimetype
from timvt.ressources.responses import TileResponse
from timvt.core import config
import asyncpg
import re

router = APIRouter()


@router.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(config.DATABASE_URL)


@router.on_event("shutdown")
async def shutdown():
    await pool.terminate()


@router.get("/ping", description="Health Check")
def ping():
    """Health check."""
    return {"ping": "pong!"}


params: Dict[str, Any] = dict(
    responses={200: {"content": {"application/x-protobuf": {}}}}
)


@router.get("/tiles/{table}/{z}/{x}/{y}\\.pbf", **params)
@router.get("/tiles/{identifier}/{table}/{z}/{x}/{y}\\.pbf", **params)
async def tile(
    table: str = Path(..., description="Table Name"),
    z: int = Path(..., ge=0, le=30, description="Tiles's zoom level"),
    x: int = Path(..., description="Tiles's column"),
    y: int = Path(..., description="Tiles's row"),
    identifier: str = Query("WebMercatorQuad", title="TMS identifier"),
) -> TileResponse:
    """Handle /tiles requests."""
    tms = morecantile.tms.get(identifier)

    bbox = tms.xy_bounds(morecantile.Tile(x, y, z))
    epsg = tms.crs.to_epsg()

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

    async with pool.acquire() as conn:
        q = await conn.prepare(sql_query)
        content = await q.fetchval(
            bbox.xmin, bbox.ymin, bbox.xmax, bbox.ymax, epsg, segSize
        )

    return TileResponse(bytes(content), media_type=mimetype["pbf"])


@router.get("/demo", **params)
@router.get("/demo/{table}", **params)
@router.get("/demo", **params)
async def demo(table: str = "countries", identifier: str = "WebMercatorQuad"):
    with open("../demo/index.html") as f:
        html = f.read()
    html = html.replace("<<<identifier>>>", identifier)
    html = html.replace("<<<table>>>", table)
    return HTMLResponse(content=html)
