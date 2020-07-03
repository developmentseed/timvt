"""TiVTiler.endpoints.demo: Demos."""

from ..templates.factory import web_template

from fastapi import APIRouter, Depends, HTTPException, Path

from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse, tags=["Demo"])
def index(
    request: Request, template=Depends(web_template),
):
    """ Return index to OpenAPI docs, Table Metadata, and Demo Pages """
    context = {"index": request.app.state.Catalog.index}
    return template(request, "index.html", context)


@router.get("/demo/{table}/", response_class=HTMLResponse, tags=["Demo"])
def demo(
    request: Request,
    table: str = Path(..., description="Table Name"),
    template=Depends(web_template),
):
    """Demo for each table."""
    if request.app.state.Catalog.get_table(table) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Table '{table}' not found.",
        )

    kwargs = {"table": table}
    tile_url = request.url_for("tilejson", **kwargs).replace("\\", "")
    context = {"endpoint": tile_url}
    return template(request, "demo.html", context)
