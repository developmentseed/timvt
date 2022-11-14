"""timvt.endpoints.factory: router factories."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type
from urllib.parse import urlencode

from morecantile import Tile, TileMatrixSet

from timvt.dependencies import (
    LayerParams,
    TileMatrixSetNames,
    TileMatrixSetParams,
    TileParams,
)
from timvt.layer import Function, Layer, Table
from timvt.models.mapbox import TileJSON
from timvt.models.OGC import TileMatrixSetList
from timvt.resources.enums import MimeTypes

from fastapi import APIRouter, Depends, Query

from starlette.datastructures import QueryParams
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response
from starlette.routing import NoMatchFound
from starlette.templating import Jinja2Templates

try:
    from importlib.resources import files as resources_files  # type: ignore
except ImportError:
    # Try backported to PY<39 `importlib_resources`.
    from importlib_resources import files as resources_files  # type: ignore


templates = Jinja2Templates(directory=str(resources_files(__package__) / "templates"))  # type: ignore

TILE_RESPONSE_PARAMS: Dict[str, Any] = {
    "responses": {200: {"content": {"application/x-protobuf": {}}}},
    "response_class": Response,
}


def queryparams_to_kwargs(q: QueryParams, ignore_keys: List = []) -> Dict:
    """Convert query params to dict."""
    keys = list(q.keys())
    values = {}
    for k in keys:
        if k in ignore_keys:
            continue

        v = q.getlist(k)
        values[k] = v if len(v) > 1 else v[0]

    return values


def _first_value(values: List[Any], default: Any = None):
    """Return the first not None value."""
    return next(filter(lambda x: x is not None, values), default)


@dataclass
class VectorTilerFactory:
    """VectorTiler Factory."""

    # FastAPI router
    router: APIRouter = field(default_factory=APIRouter)

    # TileMatrixSet dependency
    tms_dependency: Callable[..., TileMatrixSet] = TileMatrixSetParams

    # Table/Function dependency
    layer_dependency: Callable[..., Layer] = LayerParams

    with_tables_metadata: bool = False
    with_functions_metadata: bool = False
    with_viewer: bool = False

    # Router Prefix is needed to find the path for routes when prefixed
    # e.g if you mount the route with `/foo` prefix, set router_prefix to foo
    router_prefix: str = ""

    def __post_init__(self):
        """Post Init: register route and configure specific options."""
        self.register_routes()

    def register_routes(self):
        """Register Routes."""
        if self.with_tables_metadata:
            self.register_tables_metadata()

        if self.with_functions_metadata:
            self.register_functions_metadata()

        if self.with_viewer:
            self.register_viewer()

        self.register_tiles()

    def url_for(self, request: Request, name: str, **path_params: Any) -> str:
        """Return full url (with prefix) for a specific endpoint."""
        url_path = self.router.url_path_for(name, **path_params)
        base_url = str(request.base_url)
        if self.router_prefix:
            base_url += self.router_prefix.lstrip("/")
        return url_path.make_absolute_url(base_url=base_url)

    def register_tiles(self):
        """Register /tiles endpoints."""

        @self.router.get(
            "/tiles/{TileMatrixSetId}/{layer}/{z}/{x}/{y}", **TILE_RESPONSE_PARAMS
        )
        @self.router.get("/tiles/{layer}/{z}/{x}/{y}", **TILE_RESPONSE_PARAMS)
        async def tile(
            request: Request,
            tile: Tile = Depends(TileParams),
            tms: TileMatrixSet = Depends(self.tms_dependency),
            layer=Depends(self.layer_dependency),
        ):
            """Return vector tile."""
            pool = request.app.state.pool

            kwargs = queryparams_to_kwargs(
                request.query_params, ignore_keys=["tilematrixsetid"]
            )
            content = await layer.get_tile(pool, tile, tms, **kwargs)

            return Response(bytes(content), media_type=MimeTypes.pbf.value)

        @self.router.get(
            "/{TileMatrixSetId}/{layer}/tilejson.json",
            response_model=TileJSON,
            responses={200: {"description": "Return a tilejson"}},
            response_model_exclude_none=True,
        )
        @self.router.get(
            "/{layer}/tilejson.json",
            response_model=TileJSON,
            responses={200: {"description": "Return a tilejson"}},
            response_model_exclude_none=True,
        )
        async def tilejson(
            request: Request,
            layer=Depends(self.layer_dependency),
            tms: TileMatrixSet = Depends(self.tms_dependency),
            minzoom: Optional[int] = Query(
                None, description="Overwrite default minzoom."
            ),
            maxzoom: Optional[int] = Query(
                None, description="Overwrite default maxzoom."
            ),
        ):
            """Return TileJSON document."""
            path_params: Dict[str, Any] = {
                "TileMatrixSetId": tms.identifier,
                "layer": layer.id,
                "z": "{z}",
                "x": "{x}",
                "y": "{y}",
            }
            tile_endpoint = self.url_for(request, "tile", **path_params)

            qs_key_to_remove = ["tilematrixsetid", "minzoom", "maxzoom"]
            query_params = [
                (key, value)
                for (key, value) in request.query_params._list
                if key.lower() not in qs_key_to_remove
            ]

            if query_params:
                tile_endpoint += f"?{urlencode(query_params)}"

            # Get Min/Max zoom from layer settings if tms is the default tms
            if tms.identifier == layer.default_tms:
                minzoom = _first_value([minzoom, layer.minzoom])
                maxzoom = _first_value([maxzoom, layer.maxzoom])

            minzoom = minzoom if minzoom is not None else tms.minzoom
            maxzoom = maxzoom if maxzoom is not None else tms.maxzoom

            return {
                "minzoom": minzoom,
                "maxzoom": maxzoom,
                "name": layer.id,
                "bounds": layer.bounds,
                "tiles": [tile_endpoint],
            }

    def register_tables_metadata(self):
        """Register metadata endpoints."""

        @self.router.get(
            "/tables.json",
            response_model=List[Table],
            response_model_exclude_none=True,
        )
        async def tables_index(request: Request):
            """Index of tables."""

            def _get_tiles_url(id) -> Optional[str]:
                try:
                    return self.url_for(
                        request, "tile", layer=id, z="{z}", x="{x}", y="{y}"
                    )
                except NoMatchFound:
                    return None

            table_catalog = getattr(request.app.state, "table_catalog", {})
            return [
                Table(**table_info, tileurl=_get_tiles_url(table_id))
                for table_id, table_info in table_catalog.items()
            ]

        @self.router.get(
            "/table/{layer}.json",
            response_model=Table,
            responses={200: {"description": "Return table metadata"}},
            response_model_exclude_none=True,
        )
        async def table_metadata(
            request: Request,
            layer=Depends(self.layer_dependency),
        ):
            """Return table metadata."""

            def _get_tiles_url(id) -> Optional[str]:
                try:
                    return self.url_for(
                        request, "tile", layer=id, z="{z}", x="{x}", y="{y}"
                    )
                except NoMatchFound:
                    return None

            layer.tileurl = _get_tiles_url(layer.id)
            return layer

    def register_functions_metadata(self):  # noqa
        """Register function metadata endpoints."""

        @self.router.get(
            "/functions.json",
            response_model=List[Function],
            response_model_exclude_none=True,
            response_model_exclude={"sql"},
        )
        async def functions_index(request: Request):
            """Index of functions."""
            function_catalog = getattr(request.app.state, "timvt_function_catalog", {})

            def _get_tiles_url(id) -> Optional[str]:
                try:
                    return self.url_for(
                        request, "tile", layer=id, z="{z}", x="{x}", y="{y}"
                    )
                except NoMatchFound:
                    return None

            return [
                Function(
                    **func.dict(exclude_none=True), tileurl=_get_tiles_url(func.id)
                )
                for func in function_catalog.values()
            ]

        @self.router.get(
            "/function/{layer}.json",
            response_model=Function,
            responses={200: {"description": "Return Function metadata"}},
            response_model_exclude_none=True,
            response_model_exclude={"sql"},
        )
        async def function_metadata(
            request: Request,
            layer=Depends(self.layer_dependency),
        ):
            """Return table metadata."""

            def _get_tiles_url(id) -> Optional[str]:
                try:
                    return self.url_for(
                        request, "tile", layer=id, z="{z}", x="{x}", y="{y}"
                    )
                except NoMatchFound:
                    return None

            layer.tileurl = _get_tiles_url(layer.id)
            return layer

    def register_viewer(self):
        """Register viewer."""

        @self.router.get("/{layer}/viewer", response_class=HTMLResponse)
        async def demo(request: Request, layer=Depends(LayerParams)):
            """Demo for each table."""
            tile_url = self.url_for(request, "tilejson", layer=layer.id)
            if request.query_params:
                tile_url += f"?{request.query_params}"

            return templates.TemplateResponse(
                name="viewer.html",
                context={"endpoint": tile_url, "request": request},
                media_type="text/html",
            )


@dataclass
class TMSFactory:
    """TileMatrixSet endpoints Factory."""

    # Enum of supported TMS
    supported_tms: Type[TileMatrixSetNames] = TileMatrixSetNames

    # TileMatrixSet dependency
    tms_dependency: Callable[..., TileMatrixSet] = TileMatrixSetParams

    # FastAPI router
    router: APIRouter = field(default_factory=APIRouter)

    # Router Prefix is needed to find the path for /tile if the TilerFactory.router is mounted
    # with other router (multiple `.../tile` routes).
    # e.g if you mount the route with `/cog` prefix, set router_prefix to cog and
    router_prefix: str = ""

    def __post_init__(self):
        """Post Init: register route and configure specific options."""
        self.register_routes()

    def url_for(self, request: Request, name: str, **path_params: Any) -> str:
        """Return full url (with prefix) for a specific endpoint."""
        url_path = self.router.url_path_for(name, **path_params)
        base_url = str(request.base_url)
        if self.router_prefix:
            base_url += self.router_prefix.lstrip("/")
        return url_path.make_absolute_url(base_url=base_url)

    def register_routes(self):
        """Register TMS endpoint routes."""

        @self.router.get(
            r"/tileMatrixSets",
            response_model=TileMatrixSetList,
            response_model_exclude_none=True,
        )
        async def TileMatrixSet_list(request: Request):
            """
            Return list of supported TileMatrixSets.

            Specs: http://docs.opengeospatial.org/per/19-069.html#_tilematrixsets
            """
            return {
                "tileMatrixSets": [
                    {
                        "id": tms.name,
                        "title": tms.name,
                        "links": [
                            {
                                "href": self.url_for(
                                    request,
                                    "TileMatrixSet_info",
                                    TileMatrixSetId=tms.name,
                                ),
                                "rel": "item",
                                "type": "application/json",
                            }
                        ],
                    }
                    for tms in self.supported_tms
                ]
            }

        @self.router.get(
            r"/tileMatrixSets/{TileMatrixSetId}",
            response_model=TileMatrixSet,
            response_model_exclude_none=True,
        )
        async def TileMatrixSet_info(tms: TileMatrixSet = Depends(self.tms_dependency)):
            """Return TileMatrixSet JSON document."""
            return tms
