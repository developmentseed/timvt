"""timvt.endpoints.tiles: Vector Tiles endpoint."""

from timvt.dependencies import TableParams
from timvt.models.metadata import TableMetadata
from timvt.templates.factory import web_template

from fastapi import APIRouter, Depends, Request

from starlette.responses import HTMLResponse

router = APIRouter()


# We add demo viewers
@router.get("/", response_class=HTMLResponse)
def index(request: Request, template=Depends(web_template)):
    """Index of tables."""
    context = {"index": request.app.state.Catalog}
    return template(request, "index.html", context)


@router.get("/demo/{table}/", response_class=HTMLResponse)
def demo(
    request: Request,
    table: TableMetadata = Depends(TableParams),
    template=Depends(web_template),
):
    """Demo for each table."""
    tile_url = request.url_for("tilejson", table=table.id).replace("\\", "")
    context = {"endpoint": tile_url}
    return template(request, "demo.html", context)
