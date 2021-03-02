"""timvt.endpoints.demo: demo endpoint."""

from typing import List

from timvt.dependencies import TableParams
from timvt.models.metadata import TableMetadata
from timvt.templates import templates

from fastapi import APIRouter, Depends, Request

from starlette.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    """Index of tables."""
    return templates.TemplateResponse(
        name="index.html",
        context={"index": request.app.state.Catalog, "request": request},
        media_type="text/html",
    )


@router.get("/index.json", response_model=List[TableMetadata])
async def index_json(request: Request):
    """Index of tables."""
    return [TableMetadata(**r) for r in request.app.state.Catalog]


@router.get("/demo/{table}/", response_class=HTMLResponse)
async def demo(
    request: Request, table: TableMetadata = Depends(TableParams),
):
    """Demo for each table."""
    tile_url = request.url_for("tilejson", table=table.id).replace("\\", "")

    return templates.TemplateResponse(
        name="demo.html",
        context={"endpoint": tile_url, "request": request},
        media_type="text/html",
    )
