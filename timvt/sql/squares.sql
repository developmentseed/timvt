CREATE OR REPLACE
FUNCTION squares(
    xmin integer,
    ymin integer,
    xmax integer,
    ymax integer,
    epsg integer,
    depth integer default 2
)
RETURNS bytea
AS $$
DECLARE
    result bytea;
    sq_width float8;
    tile_xmin float8;
    tile_ymin float8;
    bounds geometry;
    bounds_merc geometry;
BEGIN
    -- Find the tile bounds
    bounds := ST_MakeEnvelope(xmin, ymin, xmax, ymax, epsg);

    -- Find the bottom corner of the bounds
    tile_xmin := ST_XMin(bounds);
    tile_ymin := ST_YMin(bounds);

    -- We want tile divided up into depth*depth squares per tile,
    -- so what is the width of a square?
    sq_width := (ST_XMax(bounds) - ST_XMin(bounds)) / depth;

    WITH mvtgeom AS (
        SELECT
            -- Fill in the tile with all the squares
            ST_AsMVTGeom(
                ST_SetSRID(
                    ST_MakeEnvelope(
                        tile_xmin + sq_width * (a - 1),
                        tile_ymin + sq_width * (b - 1),
                        tile_xmin + sq_width * a,
                        tile_ymin + sq_width * b
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
