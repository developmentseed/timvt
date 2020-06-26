"""TiVTiler: Template Factory."""

import os
from typing import Callable

from starlette.requests import Request
from starlette.templating import Jinja2Templates, _TemplateResponse

html_templates = Jinja2Templates(directory=os.path.dirname(__file__))


def web_template() -> Callable[[Request, str], _TemplateResponse]:
    """Create a dependency which may be injected into a FastAPI app."""

    def _template(request: Request, page: str) -> _TemplateResponse:
        """Create a template from a request"""

        scheme = request.url.scheme
        host = request.headers["host"]

        return html_templates.TemplateResponse(
            name=page,
            context={"request": request, "tile_endpoint": f"{scheme}://{host}/tiles"},
            media_type="text/html",
        )

    return _template
