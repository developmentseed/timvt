"""timvt.endpoints.tiles: Vector Tiles endpoint."""

from timvt.dependencies import TableParams
from timvt.endpoints.factory import VectorTilerFactory
from timvt.models.metadata import TableMetadata
from timvt.templates.factory import web_template

from fastapi import Depends, Request

from starlette.responses import HTMLResponse

tiler = VectorTilerFactory()


# We add demo viewers to the VectorTiler endpoints
@tiler.router.get("/", response_class=HTMLResponse, tags=["Demo"])
def index(request: Request, template=Depends(web_template)):
    """Index of tables."""
    context = {"index": request.app.state.Catalog}
    return template(request, "index.html", context)


@tiler.router.get("/demo/{table}/", response_class=HTMLResponse, tags=["Demo"])
def demo(
    request: Request,
    table: TableMetadata = Depends(TableParams),
    template=Depends(web_template),
):
    """Demo for each table."""
    tile_url = tiler.url_for(request, "tilejson", table=table.id).replace("\\", "")
    context = {"endpoint": tile_url}
    return template(request, "demo.html", context)


router = tiler.router
