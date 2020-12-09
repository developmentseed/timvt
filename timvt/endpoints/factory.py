"""TiVTiler.endpoints.factory: router factories."""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Type

from asyncpg.pool import Pool
from morecantile import TileMatrixSet

from timvt.db.tiles import VectorTileReader
from timvt.models.mapbox import TileJSON
from timvt.models.metadata import TableMetadata
from timvt.ressources.enums import MimeTypes
from timvt.utils.dependencies import TableParams, TileMatrixSetParams, _get_db_pool
from timvt.utils.timings import Timer

from fastapi import APIRouter, Depends, Path, Query

from starlette.requests import Request
from starlette.responses import Response

TILE_RESPONSE_PARAMS: Dict[str, Any] = {
    "responses": {200: {"content": {"application/x-protobuf": {}}}},
    "response_class": Response,
}


# ref: https://github.com/python/mypy/issues/5374
@dataclass  # type: ignore
class VectorTilerFactory:
    """VectorTiler Factory."""

    reader: Type[VectorTileReader] = field(default=VectorTileReader)

    # FastAPI router
    router: APIRouter = field(default_factory=APIRouter)

    # TileMatrixSet dependency
    tms_dependency: Callable[..., TileMatrixSet] = TileMatrixSetParams

    # Table dependency
    table_dependency: Callable[..., TableMetadata] = TableParams

    # Database pool dependency
    db_pool_dependency: Callable[..., Pool] = _get_db_pool

    # Router Prefix is needed to find the path for /tile if the TilerFactory.router is mounted
    # with other router (multiple `.../tile` routes).
    # e.g if you mount the route with `/cog` prefix, set router_prefix to cog and
    router_prefix: str = ""

    def __post_init__(self):
        """Post Init: register route and configure specific options."""
        self.register_routes()

    def register_routes(self):
        """Register Tiler Routes."""
        self.tile()
        self.tilejson()

    def url_for(self, request: Request, name: str, **path_params: Any) -> str:
        """Return full url (with prefix) for a specific endpoint."""
        url_path = self.router.url_path_for(name, **path_params)
        base_url = str(request.base_url)
        if self.router_prefix:
            base_url += self.router_prefix.lstrip("/")
        return url_path.make_absolute_url(base_url=base_url)

    ############################################################################
    # /tiles
    ############################################################################
    def tile(self):
        """Register /tiles endpoints."""

        @self.router.get("/tiles/{table}/{z}/{x}/{y}.pbf", **TILE_RESPONSE_PARAMS)
        @self.router.get(
            "/tiles/{TileMatrixSetId}/{table}/{z}/{x}/{y}.pbf", **TILE_RESPONSE_PARAMS
        )
        async def tile(
            z: int = Path(..., ge=0, le=30, description="Mercator tiles's zoom level"),
            x: int = Path(..., description="Mercator tiles's column"),
            y: int = Path(..., description="Mercator tiles's row"),
            tms: TileMatrixSet = Depends(self.tms_dependency),
            table: TableParams = Depends(self.table_dependency),
            db_pool: Pool = Depends(self.db_pool_dependency),
            columns: str = None,
        ):
            """Return vector tile."""
            timings = []
            headers: Dict[str, str] = {}

            reader = self.reader(db_pool, table=table, tms=tms)
            with Timer() as t:
                content = await reader.tile(x, y, z, columns=columns)
            timings.append(("db-read", t.elapsed))

            if timings:
                headers["X-Server-Timings"] = "; ".join(
                    [
                        "{} - {:0.2f}".format(name, time * 1000)
                        for (name, time) in timings
                    ]
                )

            return Response(content, media_type=MimeTypes.pbf.value, headers=headers)

    def tilejson(self):
        """Register tilejson endpoints."""

        @self.router.get(
            "/{table}.json",
            response_model=TileJSON,
            responses={200: {"description": "Return a tilejson"}},
            response_model_exclude_none=True,
        )
        @self.router.get(
            "/{TileMatrixSetId}/{table}.json",
            response_model=TileJSON,
            responses={200: {"description": "Return a tilejson"}},
            response_model_exclude_none=True,
        )
        async def tilejson(
            request: Request,
            table: TableMetadata = Depends(self.table_dependency),
            tms: TileMatrixSet = Depends(self.tms_dependency),
            minzoom: Optional[int] = Query(
                None, description="Overwrite default minzoom."
            ),
            maxzoom: Optional[int] = Query(
                None, description="Overwrite default maxzoom."
            ),
        ):
            """Return TileJSON document."""
            kwargs = {
                "TileMatrixSetId": tms.identifier,
                "table": table.id,
                "z": "{z}",
                "x": "{x}",
                "y": "{y}",
            }
            tile_endpoint = self.url_for(request, "tile", **kwargs).replace("\\", "")
            minzoom = minzoom or tms.minzoom
            maxzoom = maxzoom or tms.maxzoom
            return {
                "minzoom": minzoom,
                "maxzoom": maxzoom,
                "name": table.id,
                "tiles": [tile_endpoint],
            }
