"""timvt.resources.responses: Response models."""

import json
from typing import Any

from starlette.background import BackgroundTask
from starlette.responses import JSONResponse, Response


class JSONIndented(JSONResponse):
    """Default JSON response with indentation."""

    def render(self, content: Any) -> bytes:
        """Render response."""
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(",", ":"),
        ).encode("utf-8")


class TileResponse(Response):
    """Tiler's response."""

    def __init__(
        self,
        content: bytes,
        media_type: str,
        status_code: int = 200,
        headers: dict = {},
        background: BackgroundTask = None,
        ttl: int = 3600,
    ) -> None:
        """Init tiler response."""
        headers.update({"Content-Type": media_type})
        if ttl:
            headers.update({"Cache-Control": "max-age=3600"})
        self.body = self.render(content)
        self.status_code = 200
        self.media_type = media_type
        self.background = background
        self.init_headers(headers)
