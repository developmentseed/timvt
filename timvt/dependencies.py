"""TiVTiler.dependencies: endpoint's dependencies."""

import re
from enum import Enum

from morecantile import Tile, TileMatrixSet, tms

from timvt.layer import Layer, Table
from timvt.settings import TileSettings

from fastapi import HTTPException, Path, Query

from starlette.requests import Request

tile_settings = TileSettings()

TileMatrixSetNames = Enum(  # type: ignore
    "TileMatrixSetNames", [(a, a) for a in sorted(tms.list())]
)

default_tms = TileMatrixSetNames[tile_settings.default_tms]


def TileMatrixSetParams(
    TileMatrixSetId: TileMatrixSetNames = Query(
        default_tms,
        description=f"TileMatrixSet Name (default: '{tile_settings.default_tms}')",
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


def LayerParams(
    request: Request,
    layer: str = Path(..., description="Layer Name"),
) -> Layer:
    """Return Layer Object."""
    # Check function_catalog
    function_catalog = getattr(request.app.state, "function_catalog", {})
    func = function_catalog.get(layer)
    if func:
        return func

    # Check table_catalog
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

        table_catalog = getattr(request.app.state, "table_catalog", [])
        for r in table_catalog:
            if r["id"] == layer:
                return Table(**r)

    raise HTTPException(status_code=404, detail=f"Table/Function '{layer}' not found.")
