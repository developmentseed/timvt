
As for [`pg_tileserv`](https://github.com/CrunchyData/pg_tileserv) and [`martin`](https://github.com/urbica/martin), TiMVT can support `Function` layer/source.

Functions are database functions which ca be use to create vector tile and must of the form `function(xmin float, ymin float, xmax float, ymax: float, epsg: integer ...)`.

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
        id="squares",  # id MUST be the name of the function
        infile="...",  # PATH TO SQL FILE
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
