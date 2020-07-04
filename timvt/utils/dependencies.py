"""TiVTiler.utils.dependencies: endpoint's dependencies."""

from enum import Enum
from typing import Dict

import morecantile
from asyncpg.pool import Pool

from ..custom import tms as custom_tms

from fastapi import HTTPException, Path, Query

from starlette.requests import Request

morecantile.tms.register(custom_tms.EPSG3413)

TileMatrixSetNames = Enum(  # type: ignore
    "TileMatrixSetNames", [(a, a) for a in sorted(morecantile.tms.list())]
)


async def TileParams(
    z: int = Path(..., ge=0, le=30, description="Tiles's zoom level"),
    x: int = Path(..., description="Tiles's column"),
    y: int = Path(..., description="Tiles's row"),
) -> morecantile.Tile:
    """Tile parameters."""
    return morecantile.Tile(x, y, z)


async def TileMatrixSetParams(
    TileMatrixSetId: TileMatrixSetNames = Query(
        TileMatrixSetNames.WebMercatorQuad,  # type: ignore
        description="TileMatrixSet Name (default: 'WebMercatorQuad')",
    ),
) -> morecantile.TileMatrixSet:
    """TileMatrixSet parameters."""
    return morecantile.tms.get(TileMatrixSetId.value)


async def TableParams(
    request: Request, table: str = Path(..., description="Table Name"),
) -> Dict:
    """Table."""
    schema = None
    split = table.split(".")
    if len(split) == 2:
        schema = split[0]
        table = split[1]

    for r in request.app.state.Catalog:
        if r["table"] == table:
            if schema is None or r["schema"] == schema:
                return r

    raise HTTPException(status_code=404, detail=f"Table '{table}' not found.")


def _get_db_pool(request: Request) -> Pool:
    return request.app.state.pool
