
As for [`pg_tileserv`](https://github.com/CrunchyData/pg_tileserv) and [`martin`](https://github.com/urbica/martin), TiMVT can support `Function` layer/source.

Functions are database functions which can be use to create vector tile and must of the form `function(xmin float, ymin float, xmax float, ymax: float, epsg: integer ...)`.

## Minimal Application

```python
from timvt.db import close_db_connection, connect_to_db
from timvt.factory import VectorTilerFactory
from timvt.functions import registry as FunctionRegistry
from timvt.layer import Function

from fastapi import FastAPI, Request


# Create TiMVT Application.
app = FastAPI()

# Register Start/Stop application event handler to setup/stop the database connection
@app.on_event("startup")
async def startup_event():
    """Application startup: register the database connection and create table list."""
    await connect_to_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown: de-register the database connection."""
    await close_db_connection(app)

# Register Function to the internal registery
FunctionRegistry.register(
    Function.from_file(
        id="squares",  # By default TiMVT will call a function call `squares`
        infile="my_sql_file.sql",  # PATH TO SQL FILE
    )
)

# Register endpoints.
mvt_tiler = VectorTilerFactory(
    with_tables_metadata=True,
    with_functions_metadata=True,  # add Functions metadata endpoints (/functions.json, /{function_name}.json)
    with_viewer=True,
)
app.include_router(mvt_tiler.router, tags=["Tiles"])
```

### Function Options

When registering a `Function`, the user can set different options:

- **id** (required): name of the Layer which will then be used in the endpoint routes.
- **infile** (required): path to the SQL code
- **function_name**: name of the SQL function within the SQL code. Defaults to `id`.
- **bounds**: Bounding Box for the area of usage (this is for `documentation` only).
- **minzoom**: minimum zoom level (this is for `documentation` only).
- **maxzoom**: maximum zoom level (this is for `documentation` only).
- **options**: List of options available per function (this is for `documentation` only).

```python
# Function with Options
FunctionRegistry.register(
    Function.from_file(
        id="squares2",
        infile="my_sql_file.sql",  # PATH TO SQL FILE
        function_name="squares_but_not_squares",  # This allows to call a specific function within the SQL code
        bounds=[0.0, 0.0, 180.0, 90.0],  # overwrite default bounds
        minzoom=9,  # overwrite default minzoom
        maxzoom=24,  # overwrite default maxzoom
        options={  # Provide arguments information for documentation
            {"name": "depth", "default": 2}
        }
    )
)
```

## Function Layer Examples

#### Dynamic Geometry Example

Goal: Sub-divide input BBOX in smaller squares.

```sql
CREATE OR REPLACE FUNCTION squares(
    -- mandatory parameters
    xmin float,
    ymin float,
    xmax float,
    ymax float,
    epsg integer,
    -- additional parameters
    depth integer default 2
)
RETURNS bytea AS $$
DECLARE
    result bytea;
    sq_width float;
    bbox_xmin float;
    bbox_ymin float;
    bounds geometry;
    bounds_merc geometry;
BEGIN
    -- Find the bbox bounds
    bounds := ST_MakeEnvelope(xmin, ymin, xmax, ymax, epsg);

    -- Find the bottom corner of the bounds
    bbox_xmin := ST_XMin(bounds);
    bbox_ymin := ST_YMin(bounds);

    -- We want bbox divided up into depth*depth squares per bbox,
    -- so what is the width of a square?
    sq_width := (ST_XMax(bounds) - ST_XMin(bounds)) / depth;

    WITH mvtgeom AS (
        SELECT
            -- Fill in the bbox with all the squares
            ST_AsMVTGeom(
                ST_SetSRID(
                    ST_MakeEnvelope(
                        bbox_xmin + sq_width * (a - 1),
                        bbox_ymin + sq_width * (b - 1),
                        bbox_xmin + sq_width * a,
                        bbox_ymin + sq_width * b
                    ),
                    epsg
                ),
                bounds
            )

        -- Drive the square generator with a two-dimensional
        -- generate_series setup
        FROM generate_series(1, depth) a, generate_series(1, depth) b
    )
    SELECT ST_AsMVT(mvtgeom.*, 'default')

    -- Put the query result into the result variale.
    INTO result FROM mvtgeom;

    -- Return the answer
    RETURN result;
END;
$$
LANGUAGE 'plpgsql'
IMMUTABLE -- Same inputs always give same outputs
STRICT -- Null input gets null output
PARALLEL SAFE;
```


## Custom Function layer

So You already have an SQL `function` written but it only takes WebMercator XYZ indexes. In TiMVT we use bbox+tms to support multiple TMS but you could support simple XYZ functions by writing custom `Layer` class and dependencies.

- custom **Function** Layer

```python
# custom.py
from typing import Any
import morecantile
from buildpg import asyncpg

from timvt import layer

class Function(layer.Function):
    "Custom Function Layer: SQL function takes xyz input."""

    async def get_tile(
        self,
        pool: asyncpg.BuildPgPool,
        tile: morecantile.Tile,
        tms: morecantile.TileMatrixSet,  # tms won't be used here
        **kwargs: Any,
    ):
        """Custom Get Tile method."""
        async with pool.acquire() as conn:
            transaction = conn.transaction()
            await transaction.start()
            await conn.execute(self.sql)

            function_params = ":x, :y, :z"
            if kwargs:
                params = ", ".join([f"{k} => {v}" for k, v in kwargs.items()])
                function_params += f", {params}"

            content = await conn.fetchval_b(
                f"SELECT {self.function_name}({function_params})",
                x=tile.x,
                y=tile.y,
                z=tile.z,
            )

            await transaction.rollback()

        return content
```

- custom **registery**, referencing the custom Function
```python
# custom_registery.py
from dataclasses import dataclass
from typing import ClassVar, Dict

from .custom import Function

@dataclass
class Registry:
    """function registry"""

    funcs: ClassVar[Dict[str, Function]] = {}

    @classmethod
    def get(cls, key: str):
        """lookup function by name"""
        return cls.funcs.get(key)

    @classmethod
    def register(cls, *args: Function):
        """register function(s)"""
        for func in args:
            cls.funcs[func.id] = func


registry = Registry()
```

- custom **dependencies**

```python
# custom_dependencies.py
import re
from enum import Enum

from fastapi import HTTPException, Path
from starlette.requests import Request
from morecantile import TileMatrixSet, tms
from timvt.layer import Layer

from .custom_registery import registry as FunctionRegistry


# Custom TileMatrixSets deps (only support WebMercatorQuad)
TileMatrixSetNames = Enum(  # type: ignore
    "TileMatrixSetNames", [("WebMercatorQuad", "WebMercatorQuad")]
)

def TileMatrixSetParams(
    TileMatrixSetId: TileMatrixSetNames = Query(
        TileMatrixSetNames.WebMercatorQuad,  # type: ignore
        description="TileMatrixSet Name",
    ),
) -> TileMatrixSet:
    """TileMatrixSet parameters."""
    return tms.get(TileMatrixSetId.name)


# Custom Layer Params
def LayerParams(
    request: Request, layer: str = Path(..., description="Layer Name"),
) -> Layer:
    """Return Layer Object."""
    func = FunctionRegistry.get(layer)
    if func:
        return func
    else:
        table_pattern = re.match(  # type: ignore
            r"^(?P<schema>.+)\.(?P<table>.+)$", layer
        )
        if not table_pattern:
            raise HTTPException(
                status_code=404, detail=f"Invalid Table format '{layer}'."
            )

        assert table_pattern.groupdict()["schema"]
        assert table_pattern.groupdict()["table"]

        for r in request.app.state.table_catalog:
            if r["id"] == layer:
                return Table(**r)

    raise HTTPException(status_code=404, detail=f"Table/Function '{layer}' not found.")
```

- Custom **Application**
```python
# custom_app.py
from timvt.db import close_db_connection, connect_to_db
from timvt.factory import TMSFactory, VectorTilerFactory

from fastapi import FastAPI

from .custom_dependencies import LayerParams, TileMatrixSetParams, TileMatrixSetNames

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """Application startup: register the database connection and create table list."""
    await connect_to_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown: de-register the database connection."""
    await close_db_connection(app)


# Register endpoints.
mvt_tiler = VectorTilerFactory(
    with_tables_metadata=True,
    with_functions_metadata=True,
    with_viewer=True,
    tms_dependency=TileMatrixSetParams,
    layer_dependency=LayerParams,
)
app.include_router(mvt_tiler.router)

tms = TMSFactory(supported_tms=TileMatrixSetNames, tms_dependency=TileMatrixSetParams)
app.include_router(tms.router, tags=["TileMatrixSets"])
```
