# Release Notes

## 0.8.0a3 (2023-03-14)

* fix factories `url_for` type (for starlette >=0.26)

## 0.8.0a2 (2022-12-14)

* replace `VectorTilerFactory.tms_dependency` attribute by `TilerFactory.supported_tms`. This attribute gets a `morecantile.defaults.TileMatrixSets` store and will create the tms dependencies dynamically
* replace `TMSFactory.tms_dependency` attribute by `TMSFactory.supported_tms`. This attribute gets a `morecantile.defaults.TileMatrixSets` store and will create the tms dependencies dynamically
* add `default_tms` in `VectorTilerFactory` to set the default TMS identifier supported by the tiler (e.g `WebMercatorQuad`)

## 0.8.0a1 (2022-11-21)

* update hatch config

## 0.8.0a0 (2022-11-16)

* remove `.pbf` extension in tiles endpoints
* add `orjson` as an optional dependency (for faster JSON encoding/decoding within the database communication)
* enable `geom` query parameter to select the `geometry column` (defaults to the first one)
* add FastAPI application `exception handler` in default app
* add `CacheControlMiddleware` middleware
* enable more options to be forwarded to the `asyncpg` pool creation
* add `PG_SCHEMAS` and `PG_TABLES` environment variable to specify Postgres schemas and tables
* add `TIMVT_FUNCTIONS_DIRECTORY` environment variable to look for function SQL files
* switch viewer to Maplibre
* add `Point` and `LineString` feature support in viewer
* Update dockerfiles to python3.10 and postgres14-postgis3.3
* update FastAPI requirement to >0.87
* remove endpoint Tags
* make orjson a default requirement

**breaking changes**

* renamed `app.state.function_catalog` to `app.state.timvt_function_catalog`
* changed `timvt.layer.Table` format
* `table_catalog` is now of `Dict[str, Dict[str, Any]]` type (instead of `List[Dict[str, Any]]`)
* renamed `timvt.db.table_index` to `timvt.dbmodel.get_table_index`
* default to only view tables within the `public` schema
* renamed *base exception class* to `TiMVTError`
* remove python 3.7 support

## 0.7.0 (2022-06-09)

* update database settings input
* add `default_tms` in Layer definition to specify the Min/Max zoom TileMatrixSet
* update `starlette-cramjam` requirement

**breaking changes**

* deprecating the use of `.pbf` in tile's path

## 0.6.0 (2022-04-14)

* update `morecantile` requirement to `>3.1,=<4.0`

## 0.5.0 (2022-04-13)

* switch to `pyproject.toml` and repo cleanup

## 0.4.1 (2022-02-10)

* update viewer

## 0.4.0 (2022-02-10)

* Refactor Function Registry to be hosted in the application state (`app.state.function_catalog) as the Table catalog.
* move `timvt.function.Registry` to `timvt.layer.FunctionRegistry`

## 0.3.0 (2022-02-09)

* update settings management from starlette to pydantic and use `TIMVT_` prefix

## 0.2.1 (2022-01-25)

* update FastAPI version requirement to allow `>=0.73`

## 0.2.0 (2022-01-05)

* Faster and cleaner SQL code
* Compare Tile and Table geometries in Table CRS (speedup)
* Allow non-epsg based TileMatrixSet
* update morecantile requirement to `>=3.0.2`
* add `geometry_srid` in Table metadata
* refactor `Function` layers.

**breaking changes**

* Function layer signature change
```sql
-- before
CREATE FUNCTION name(
    -- bounding box
    xmin float,
    ymin float,
    xmax float,
    ymax float,
    -- EPSG (SRID) of the bounding box coordinates
    epsg integer,
    -- additional parameters
    value0 int,
    value1 int
)
RETURNS bytea

-- now
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

## 0.1.0 (2021-10-12)

Initial release
