# Release Notes

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
