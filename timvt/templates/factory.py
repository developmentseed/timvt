"""TiVTiler: Template Factory."""

import logging
import os
from typing import Callable, Dict

from starlette.requests import Request
from starlette.templating import Jinja2Templates, _TemplateResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

html_templates = Jinja2Templates(directory=os.path.dirname(__file__))


def web_template() -> Callable[[Request, str], _TemplateResponse]:
    """Create a dependency which may be injected into a FastAPI app."""

    def _template(request: Request, page: str, context: Dict = {}) -> _TemplateResponse:
        """Create a template from a request"""
        context["request"] = request
        return html_templates.TemplateResponse(
            name=page, context=context, media_type="text/html",
        )

    return _template
