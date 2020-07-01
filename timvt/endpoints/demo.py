"""TiVTiler.endpoints.demo: Demos."""

from ..templates.factory import web_template

from fastapi import APIRouter, Depends, Path

from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse, tags=["demo"])
def index(
    request: Request, template=Depends(web_template),
):
    context = {"index": request.app.state.Catalog.index}
    return template(request, "index.html", context)


@router.get("/demo/{table}/", response_class=HTMLResponse, tags=["demo"])
def demo(
    request: Request,
    table: str = Path(..., description="Table Name"),
    template=Depends(web_template),
):
    """Demo."""
    table_idx = request.app.state.Catalog.get_table(table)
    if table_idx is None:
        error = {"error": "Table not found"}
        return JSONResponse(content=error, status_code=404)

    for route in request.scope["router"].routes:
        if route.name == "tile_3857":
            tile_path = route.path.format(table=table, x="{x}", y="{y}", z="{z}")

    context = {"table": table, "tile_path": tile_path}
    return template(request, "demo.html", context)
