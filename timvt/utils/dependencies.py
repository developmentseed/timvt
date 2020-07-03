"""TiVTiler.utils.dependencies: endpoint's dependencies."""

from enum import Enum

import morecantile
from asyncpg.pool import Pool

from ..custom import tms as custom_tms

from fastapi import Path, Query

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


def _get_db_pool(request: Request) -> Pool:
    return request.app.state.pool
