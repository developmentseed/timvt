"""TiVTiler.endpoints.demo: Demos."""

from typing import Dict

from ..templates.factory import web_template
from ..utils.dependencies import TableParams

from fastapi import APIRouter, Depends

from starlette.requests import Request
from starlette.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse, tags=["Demo"])
def index(
    request: Request, template=Depends(web_template),
):
    """ Return index to OpenAPI docs, Table Metadata, and Demo Pages """
    context = {"index": request.app.state.Catalog}
    return template(request, "index.html", context)


@router.get("/demo/{table}/", response_class=HTMLResponse, tags=["Demo"])
def demo(
    request: Request,
    table: Dict = Depends(TableParams),
    template=Depends(web_template),
):
    """Demo for each table."""
    kwargs = {"table": table["table"]}
    tile_url = request.url_for("tilejson", **kwargs).replace("\\", "")
    context = {"endpoint": tile_url}
    return template(request, "demo.html", context)
