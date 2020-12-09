"""TiVTiler.endpoints.tiles: Vector Tiles endpoint."""

from timvt.endpoints.factory import VectorTilerFactory
from timvt.templates.factory import web_template

from ..models.metadata import TableMetadata
from ..utils.dependencies import TableParams

from fastapi import Depends, Request

from starlette.responses import HTMLResponse

tiler = VectorTilerFactory()
router = tiler.router


@router.get("/", response_class=HTMLResponse, tags=["Demo"])
def index(request: Request, template=Depends(web_template)):
    """Index of tables."""
    context = {"index": request.app.state.Catalog}
    return template(request, "index.html", context)


@router.get("/demo/{table}/", response_class=HTMLResponse, tags=["Demo"])
def demo(
    request: Request,
    table: TableMetadata = Depends(TableParams),
    template=Depends(web_template),
):
    """Demo for each table."""
    tile_url = tiler.url_for(request, "tilejson", table=table.id).replace("\\", "")
    context = {"endpoint": tile_url}
    return template(request, "demo.html", context)
