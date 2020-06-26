"""TiVTiler.endpoints.demo: Demos."""

from ..templates.factory import web_template

from fastapi import APIRouter, Depends

from starlette.requests import Request
from starlette.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse, tags=["demo"])
def demo(request: Request, template=Depends(web_template)):
    """Demo."""
    return template(request, "index.html")
