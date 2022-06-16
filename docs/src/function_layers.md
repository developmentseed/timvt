
As for [`pg_tileserv`](https://github.com/CrunchyData/pg_tileserv) and [`martin`](https://github.com/urbica/martin), TiMVT can support `Function` layer/source.

`Functions` are database functions which can be used to create vector tiles and must of the form:

```sql
CREATE FUNCTION name(
    -- bounding box
    xmin float,
    ymin float,
    xmax float,
    ymax float,
    -- EPSG (SRID) of the bounding box coordinates
    epsg integer,
    -- additional parameters
    query_params json
)
RETURNS bytea
```

Argument     | Type  | Description
------------ | ----- | -----------------------
xmin         | float | left coordinate
ymin         | float | bottom coordinate
xmax         | float | right coordinate
ymax         | float | top coordinate
epsg         | float | bounding box EPSG (SRID) number
query_params | json  | Additional Query string parameters

### Query Parameters

`TiMVT` will forward all query parameters to the function as a JSON object. It's on the user to properly parse the JSON object in the database function.

```python
url = "https://endpoint/tiles/my_function/1/1/1?value1=2&value2=3"
query_params = '{"value1": "2", "value2": "3"}'

url = "https://endpoint/tiles/my_function/1/1/1?v=2&v=3"
query_params = '{"v": ["2", "3"]}'
```
!!! important

    `Functions` are not *hard coded* into the database but dynamically registered/unregistered by the application on each tile call.

## Minimal Application

```python
from timvt.db import close_db_connection, connect_to_db
from timvt.factory import VectorTilerFactory
from timvt.layer import FunctionRegistry
from timvt.layer import Function

from fastapi import FastAPI, Request


# Create FastAPI Application.
app = FastAPI()

# Add Function registery to the application state
app.state.timvt_function_catalog = FunctionRegistry()

# Register Start/Stop application event handler to setup/stop the database connection
# and populate `app.state.table_catalog`
@app.on_event("startup")
async def startup_event():
    """Application startup: register the database connection and create table list."""
    await connect_to_db(app)

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown: de-register the database connection."""
    await close_db_connection(app)

# Register Function to the application internal registry
app.state.timvt_function_catalog.register(
    Function.from_file(
        id="squares",  # By default TiMVT will call a function call `squares`
        infile="my_sql_file.sql",  # PATH TO SQL FILE
    )
)

# Register endpoints
mvt_tiler = VectorTilerFactory(
    with_tables_metadata=True,
    with_functions_metadata=True,  # add Functions metadata endpoints (/functions.json, /{function_name}.json)
    with_viewer=True,
)
app.include_router(mvt_tiler.router)
```

!!! Important

    A function `Registry` object (timvt.layer.FunctionRegistry) should be initialized and stored within the application **state**. TiMVT assumes `app.state.timvt_function_catalog` is where the registry is.

## Function Options

When registering a `Function`, the user can set different options:

- **id** (required): name of the Layer which will then be used in the endpoint routes.
- **sql** (required): SQL code
- **function_name**: name of the SQL function within the SQL code. Defaults to `id`.
- **bounds**: Bounding Box for the area of usage (this is for `documentation` only).
- **minzoom**: minimum zoom level (this is for `documentation` only).
- **maxzoom**: maximum zoom level (this is for `documentation` only).
- **options**: List of options available per function (this is for `documentation` only).

```python
from timvt.layer import Function


# Function with Options
Function(
    id="squares2",
    sql="""
        CREATE FUNCTION squares_but_not_squares(
            xmin float,
            ymin float,
            xmax float,
            ymax float,
            epsg integer,
            query_params json
        )
        RETURNS bytea AS $$
        ...
    """,
    function_name="squares_but_not_squares",  # This allows to call a specific function within the SQL code
    bounds=[0.0, 0.0, 180.0, 90.0],  # overwrite default bounds
    minzoom=9,  # overwrite default minzoom
    maxzoom=24,  # overwrite default maxzoom
    options={  # Provide arguments information for documentation
        {"name": "depth", "default": 2}
    }
)

# Using `from_file` class method
Function.from_file(
    id="squares2",
    infile="directory/my_sql_file.sql",  # PATH TO SQL FILE
    function_name="squares_but_not_squares",  # This allows to call a specific function within the SQL code
    bounds=[0.0, 0.0, 180.0, 90.0],  # overwrite default bounds
    minzoom=9,  # overwrite default minzoom
    maxzoom=24,  # overwrite default maxzoom
    options={  # Provide arguments information for documentation
        {"name": "depth", "default": 2}
    }
)
```

## Function Layer Examples

### Dynamic Geometry Example

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
    query_params json
)
RETURNS bytea AS $$
DECLARE
    result bytea;
    sq_width float;
    bbox_xmin float;
    bbox_ymin float;
    bounds geometry;
    depth integer;
BEGIN
    -- Find the bbox bounds
    bounds := ST_MakeEnvelope(xmin, ymin, xmax, ymax, epsg);

    -- Find the bottom corner of the bounds
    bbox_xmin := ST_XMin(bounds);
    bbox_ymin := ST_YMin(bounds);

    -- Get Depth from the query_params object
    depth := coalesce((query_params ->> 'depth')::int, 2);

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

## Extending the Function layer

As mentioned early, `Function` takes bounding box and EPSG number as input to support multiple TileMatrixSet. If you only want to support one `pre-defined` TMS (e.g `WebMercator`) you could have functions taking `X,Y,Z` inputs:

Example of XYZ function:
```sql
CREATE OR REPLACE FUNCTION xyz(
    z integer,
    x integer,
    y integer,
    query_params json
)
RETURNS bytea
AS $$
DECLARE
    table_name text;
    result bytea;
BEGIN
    table_name := query_params ->> 'table';

    WITH
    bounds AS (
      SELECT ST_TileEnvelope(z, x, y) AS geom
    ),
    mvtgeom AS (
      SELECT ST_AsMVTGeom(ST_Transform(t.geom, 3857), bounds.geom) AS geom, t.name
      FROM table_name t, bounds
      WHERE ST_Intersects(t.geom, ST_Transform(bounds.geom, 4326))
    )
    SELECT ST_AsMVT(mvtgeom, table_name)
    INTO result
    FROM mvtgeom;

    RETURN result;
END;
$$
LANGUAGE 'plpgsql'
STABLE
PARALLEL SAFE;
```

In order to support those function, you'll need to `extend` the `Funcion` class:

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

            sql_query = clauses.Select(
                Func(
                    self.function_name,
                    ":x",
                    ":y",
                    ":z",
                    ":query_params",
                ),
            )
            q, p = render(
                str(sql_query),
                x=tile.x,
                y=tile.y,
                z=tile.z,
                query_params=json.dumps(kwargs),
            )

            # execute the query
            content = await conn.fetchval(q, *p)

            # rollback
            await transaction.rollback()

        return content
```
