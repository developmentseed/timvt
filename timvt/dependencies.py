"""TiVTiler.dependencies: endpoint's dependencies."""

import re
from enum import Enum

import morecantile

from timvt.functions import registry as FunctionRegistry
from timvt.layer import Layer, Table

from fastapi import HTTPException, Path, Query

from starlette.requests import Request

TileMatrixSetNames = Enum(  # type: ignore
    "TileMatrixSetNames", [(a, a) for a in sorted(morecantile.tms.list())]
)


def TileMatrixSetParams(
    TileMatrixSetId: TileMatrixSetNames = Query(
        TileMatrixSetNames.WebMercatorQuad,  # type: ignore
        description="TileMatrixSet Name (default: 'WebMercatorQuad')",
    ),
) -> morecantile.TileMatrixSet:
    """TileMatrixSet parameters."""
    return morecantile.tms.get(TileMatrixSetId.name)


def TileParams(
    z: int = Path(..., ge=0, le=30, description="Tiles's zoom level"),
    x: int = Path(..., description="Tiles's column"),
    y: int = Path(..., description="Tiles's row"),
) -> morecantile.Tile:
    """Tile parameters."""
    return morecantile.Tile(x, y, z)


def LayerParams(
    request: Request,
    layer: str = Path(..., description="Layer Name"),
) -> Layer:
    """Return Layer Object."""
    func = FunctionRegistry.get(layer)
    if func:
        return func
    else:
        table_pattern = re.match(  # type: ignore
            r"^(?P<schema>.+)\.(?P<table>.+)$", layer
        )
        if not table_pattern:
            raise HTTPException(
                status_code=404, detail=f"Invalid Table format '{layer}'."
            )

        assert table_pattern.groupdict()["schema"]
        assert table_pattern.groupdict()["table"]

        for r in request.app.state.table_catalog:
            if r["id"] == layer:
                return Table(**r)

    raise HTTPException(status_code=404, detail=f"Table/Function '{layer}' not found.")
