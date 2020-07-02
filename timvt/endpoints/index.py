"""TiVTiler.index: Index endpoint."""

from typing import Any, Dict

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

params: Dict[str, Any] = {
    "responses": {200: {"content": {"application/json": {}}}},
    "response_class": JSONResponse,
    "tags": ["Index"],
}


@router.get("/index", **params)
async def display_index(request: Request,) -> JSONResponse:
    """ Return JSON with available table metadata. """
    return JSONResponse(content=request.app.state.Catalog.index)
