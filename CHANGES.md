# Release Notes

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
