"""TiVTiler.dependencies: endpoint's dependencies."""

import re
from enum import Enum

from asyncpg.pool import Pool
from morecantile import Tile, TileMatrixSet, tms

from timvt.custom import tms as custom_tms
from timvt.models.metadata import TableMetadata

from fastapi import HTTPException, Path, Query

from starlette.requests import Request

# Register Custom TMS
tms = tms.register([custom_tms.EPSG3413, custom_tms.EPSG6933])

TileMatrixSetNames = Enum(  # type: ignore
    "TileMatrixSetNames", [(a, a) for a in sorted(tms.list())]
)


def TileParams(
    z: int = Path(..., ge=0, le=30, description="Tiles's zoom level"),
    x: int = Path(..., description="Tiles's column"),
    y: int = Path(..., description="Tiles's row"),
) -> Tile:
    """Tile parameters."""
    return Tile(x, y, z)


def TileMatrixSetParams(
    TileMatrixSetId: TileMatrixSetNames = Query(
        TileMatrixSetNames.WebMercatorQuad,  # type: ignore
        description="TileMatrixSet Name (default: 'WebMercatorQuad')",
    ),
) -> TileMatrixSet:
    """TileMatrixSet parameters."""
    return tms.get(TileMatrixSetId.name)


def TableParams(
    request: Request, table: str = Path(..., description="Table Name"),
) -> TableMetadata:
    """Table."""
    table_pattern = re.match(  # type: ignore
        r"^((?P<schema>.+)\.)?(?P<table>.+)$", table
    ).groupdict()

    schema = table_pattern["schema"]
    table_name = table_pattern["table"]

    for r in request.app.state.Catalog:
        if r["table"] == table_name:
            if schema is None or r["schema"] == schema:
                return TableMetadata(**r)

    raise HTTPException(status_code=404, detail=f"Table '{table}' not found.")


def _get_db_pool(request: Request) -> Pool:
    return request.app.state.pool
