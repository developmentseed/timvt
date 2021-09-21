"""TiVTiler.dependencies: endpoint's dependencies."""

import re
from enum import Enum

from morecantile import Tile, TileMatrixSet, tms

from timvt.models.metadata import TableMetadata

from fastapi import HTTPException, Path, Query

from starlette.requests import Request

TileMatrixSetNames = Enum(  # type: ignore
    "TileMatrixSetNames", [(a, a) for a in sorted(tms.list())]
)


def TileMatrixSetParams(
    TileMatrixSetId: TileMatrixSetNames = Query(
        TileMatrixSetNames.WebMercatorQuad,  # type: ignore
        description="TileMatrixSet Name (default: 'WebMercatorQuad')",
    ),
) -> TileMatrixSet:
    """TileMatrixSet parameters."""
    return tms.get(TileMatrixSetId.name)


def TileParams(
    z: int = Path(..., ge=0, le=30, description="Tiles's zoom level"),
    x: int = Path(..., description="Tiles's column"),
    y: int = Path(..., description="Tiles's row"),
) -> Tile:
    """Tile parameters."""
    return Tile(x, y, z)


def TableParams(
    request: Request, table: str = Path(..., description="Table Name"),
) -> TableMetadata:
    """Table."""
    table_pattern = re.match(  # type: ignore
        r"^(?P<schema>.+)\.(?P<table>.+)$", table
    ).groupdict()

    assert table_pattern["schema"]
    assert table_pattern["table"]

    for r in request.app.state.table_catalog:
        if r["id"] == table:
            return TableMetadata(**r)

    raise HTTPException(status_code=404, detail=f"Table '{table}' not found.")
