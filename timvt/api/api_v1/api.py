"""timvt api."""

from typing import Any, Dict

from fastapi import APIRouter, Depends
from fastapi import Path, Query
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

import morecantile

from timvt.ressources.common import mimetype
from timvt.ressources.responses import TileResponse
from timvt.api import deps

from .utils import getMVT


router = APIRouter()


@router.get("/ping", description="Health Check")
def ping():
    """Health check."""
    return {"ping": "pong!"}


params: Dict[str, Any] = dict(
    responses={200: {"content": {"application/x-protobuf": {}}}}
)


@router.get("/tiles/{table}/{z}/{x}/{y}\\.pbf", **params)
@router.get("/tiles/{identifier}/{table}/{z}/{x}/{y}\\.pbf", **params)
def tile(
    db: Session = Depends(deps.get_db),
    table: str = Path(..., description="Table Name"),
    z: int = Path(..., ge=0, le=30, description="Tiles's zoom level"),
    x: int = Path(..., description="Tiles's column"),
    y: int = Path(..., description="Tiles's row"),
    identifier: str = Query("WebMercatorQuad", title="TMS identifier"),
) -> TileResponse:
    """Handle /tiles requests."""
    tms = morecantile.tms.get(identifier)

    bbox = tms.xy_bounds(morecantile.Tile(x, y, z))
    epsg_number = tms.crs.to_epsg()

    content = getMVT(db, bbox, epsg_number, table)

    return TileResponse(bytes(content), media_type=mimetype["pbf"])

@router.get("/demo", **params)
async def demo():
    return FileResponse("../demo/index.html")
