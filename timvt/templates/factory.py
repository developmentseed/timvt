"""TiVTiler: Template Factory."""

import pathlib
from typing import Callable, Dict

from starlette.requests import Request
from starlette.templating import Jinja2Templates, _TemplateResponse

templates = Jinja2Templates(directory=str(pathlib.Path(__file__).parent))


def web_template() -> Callable[[Request, str], _TemplateResponse]:
    """Create a dependency which may be injected into a FastAPI app."""

    def _template(request: Request, page: str, context: Dict = {}) -> _TemplateResponse:
        """Create a template from a request"""
        context["request"] = request
        return templates.TemplateResponse(
            name=page, context=context, media_type="text/html",
        )

    return _template
