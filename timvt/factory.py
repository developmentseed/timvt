"""timvt.endpoints.factory: router factories."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type
from urllib.parse import urlencode

from morecantile import TileMatrixSet

from timvt.dependencies import (
    TableParams,
    TileMatrixSetNames,
    TileMatrixSetParams,
    TileParams,
)
from timvt.models.mapbox import TileJSON
from timvt.models.metadata import TableMetadata
from timvt.models.OGC import TileMatrixSetList
from timvt.resources.enums import MimeTypes
from timvt.settings import MAX_FEATURES_PER_TILE, TILE_BUFFER, TILE_RESOLUTION

from fastapi import APIRouter, Depends, Query

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


@dataclass
class VectorTilerFactory:
    """VectorTiler Factory."""

    # FastAPI router
    router: APIRouter = field(default_factory=APIRouter)

    # TileMatrixSet dependency
    tms_dependency: Callable[..., TileMatrixSet] = TileMatrixSetParams

    # Table dependency
    table_dependency: Callable[..., TableMetadata] = TableParams

    # Router Prefix is needed to find the path for routes when prefixed
    # e.g if you mount the route with `/foo` prefix, set router_prefix to foo
    router_prefix: str = ""

    def __post_init__(self):
        """Post Init: register route and configure specific options."""
        self.register_routes()

    def register_routes(self):
        """Register Routes."""
        self.tile()
        self.metadata()
        self.viewer()

    def url_for(self, request: Request, name: str, **path_params: Any) -> str:
        """Return full url (with prefix) for a specific endpoint."""
        url_path = self.router.url_path_for(name, **path_params)
        base_url = str(request.base_url)
        if self.router_prefix:
            base_url += self.router_prefix.lstrip("/")
        return url_path.make_absolute_url(base_url=base_url)

    def tile(self):
        """Register /tiles endpoints."""

        @self.router.get("/tiles/{table}/{z}/{x}/{y}.pbf", **TILE_RESPONSE_PARAMS)
        @self.router.get(
            "/tiles/{TileMatrixSetId}/{table}/{z}/{x}/{y}.pbf", **TILE_RESPONSE_PARAMS
        )
        async def tile(
            request: Request,
            tile: TileParams = Depends(),
            tms: TileMatrixSet = Depends(self.tms_dependency),
            table: TableMetadata = Depends(self.table_dependency),
            columns: Optional[str] = Query(
                None,
                description="Comma-seprated list of properties (column's name) to include in the tile",
            ),
            limit: Optional[int] = Query(
                None,
                description=f"Number of features to write to a tile. Defaults to {MAX_FEATURES_PER_TILE}.",
            ),
            resolution: Optional[int] = Query(
                None, description=f"Tile's resolution. Defaults to {TILE_RESOLUTION}.",
            ),
            buffer: Optional[int] = Query(
                None,
                description=f"Size of extra data to add for a tile. Defaults to {TILE_BUFFER}.",
            ),
        ):
            """Return vector tile."""
            pool = request.app.state.pool

            limit = limit if limit is not None else MAX_FEATURES_PER_TILE
            limitstr = f"LIMIT {limit}" if limit > -1 else ""

            resolution = resolution if resolution is not None else TILE_RESOLUTION
            buffer = buffer if buffer is not None else TILE_BUFFER

            # create list of columns to return
            geometry_column = table.geometry_column
            cols = table.properties
            if geometry_column in cols:
                del cols[geometry_column]
            if columns is not None:
                include_cols = [c.strip() for c in columns.split(",")]
                for c in cols.copy():
                    if c not in include_cols:
                        del cols[c]
            colstring = ", ".join(list(cols))

            bbox = tms.xy_bounds(tile)
            epsg = tms.crs.to_epsg()
            segSize = bbox.right - bbox.left

            async with pool.acquire() as conn:
                sql_query = f"""
                    WITH
                    bounds AS (
                        SELECT
                            ST_Segmentize(
                                ST_MakeEnvelope(
                                    :xmin,
                                    :ymin,
                                    :xmax,
                                    :ymax,
                                    :epsg
                                ),
                                :seg_size
                            ) AS geom
                    ),
                    mvtgeom AS (
                        SELECT ST_AsMVTGeom(
                            ST_Transform(t.{geometry_column}, :epsg),
                            bounds.geom,
                            :tile_resolution,
                            :tile_buffer
                        ) AS geom, {colstring}
                        FROM {table.id} t, bounds
                        WHERE ST_Intersects(
                            ST_Transform(t.{geometry_column}, 4326),
                            ST_Transform(bounds.geom, 4326)
                        ) {limitstr}
                    )
                    SELECT ST_AsMVT(mvtgeom.*) FROM mvtgeom
                """

                content = await conn.fetchval_b(
                    sql_query,
                    xmin=bbox.left,
                    ymin=bbox.bottom,
                    xmax=bbox.right,
                    ymax=bbox.top,
                    epsg=epsg,
                    seg_size=segSize,
                    tile_resolution=resolution,
                    tile_buffer=buffer,
                )

            return Response(bytes(content), media_type=MimeTypes.pbf.value)

            @self.router.get(
                "/{table}/tilejson.json",
                response_model=TileJSON,
                responses={200: {"description": "Return a tilejson"}},
                response_model_exclude_none=True,
            )
            @self.router.get(
                "/{TileMatrixSetId}/{table}/tilejson.json",
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
                columns: Optional[str] = Query(
                    None,
                    description="Comma-seprated list of properties (column's name) to include in the tile",
                ),
                limit: Optional[int] = Query(
                    None,
                    description=f"Number of features to write to a tile. Defaults to {MAX_FEATURES_PER_TILE}.",
                ),
                resolution: Optional[int] = Query(
                    None,
                    description=f"Tile's resolution. Defaults to {TILE_RESOLUTION}.",
                ),
                buffer: Optional[int] = Query(
                    None,
                    description=f"Size of extra data to add for a tile. Defaults to {TILE_BUFFER}.",
                ),
            ):
                """Return TileJSON document."""
                kwargs: Dict[str, Any] = {
                    "TileMatrixSetId": tms.identifier,
                    "table": table.id,
                    "z": "{z}",
                    "x": "{x}",
                    "y": "{y}",
                }
                tile_endpoint = self.url_for(request, "tile", **kwargs).replace(
                    "\\", ""
                )

                qs = [
                    (key, value)
                    for (key, value) in [
                        ("columns", columns),
                        ("limit", limit),
                        ("resolution", resolution),
                        ("buffer", buffer),
                    ]
                    if value is not None
                ]

                if qs:
                    tile_endpoint += f"?{urlencode(qs)}"

                minzoom = (
                    minzoom if minzoom is not None else (table.minzoom or tms.minzoom)
                )
                maxzoom = (
                    maxzoom if maxzoom is not None else (table.maxzoom or tms.maxzoom)
                )

                return {
                    "minzoom": minzoom,
                    "maxzoom": maxzoom,
                    "name": table.id,
                    "bounds": table.bounds,
                    "tiles": [tile_endpoint],
                }

    def metadata(self):
        """Register metadata endpoints."""

        @self.router.get(
            "/index.json",
            response_model=List[TableMetadata],
            response_model_exclude_none=True,
        )
        async def index_json(request: Request):
            """Index of tables."""

            def _get_tiles_url(id) -> str:
                kwargs = {
                    "table": id,
                    "z": "{z}",
                    "x": "{x}",
                    "y": "{y}",
                }
                try:
                    return self.url_for(request, "tile", **kwargs)
                except NoMatchFound:
                    return None

            return [
                TableMetadata(**r, tileurl=_get_tiles_url(r["id"]))
                for r in request.app.state.table_catalog
            ]

        @self.router.get(
            "/{table}.json",
            response_model=TableMetadata,
            responses={200: {"description": "Return table metadata"}},
            response_model_exclude_none=True,
        )
        async def metadata(
            request: Request, table: TableMetadata = Depends(self.table_dependency)
        ):
            """Return table metadata."""

            def _get_tiles_url(id) -> str:
                kwargs = {
                    "table": id,
                    "z": "{z}",
                    "x": "{x}",
                    "y": "{y}",
                }
                try:
                    return self.url_for(request, "tile", **kwargs)
                except NoMatchFound:
                    return None

            table.tileurl = _get_tiles_url(table.id)
            return table

    def viewer(self):
        """Register viewer."""

        @self.router.get("/viewer/{table}", response_class=HTMLResponse)
        async def demo(
            request: Request, table: TableMetadata = Depends(TableParams),
        ):
            """Demo for each table."""
            tile_url = request.url_for("tilejson", table=table.id).replace("\\", "")

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
