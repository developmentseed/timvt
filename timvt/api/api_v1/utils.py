

from sqlalchemy.orm import Session

import morecantile


def getMVT(
    db: Session,
    bbox: morecantile.CoordsBbox,
    epsg: int,
    table: str,
    densify: int = 4,
) -> bytes:
    """Fetch and Create MVT."""
    segSize = (bbox.xmax - bbox.xmin) / densify
    sql_tmpl = f"ST_Segmentize(ST_MakeEnvelope({bbox.xmin}, {bbox.ymin}, {bbox.xmax}, {bbox.ymax}, {epsg}),{segSize})"
    sql_query = f"""
        WITH
        bounds AS (
            SELECT {sql_tmpl} AS geom,
                    {sql_tmpl}::box2d AS b2d
        ),
        mvtgeom AS (
            SELECT ST_AsMVTGeom(ST_Transform(t.geom, {epsg}), bounds.b2d) AS geom, *
            FROM {table} t, bounds
            WHERE ST_Intersects(t.geom, ST_Transform(bounds.geom, 4326))
        )
        SELECT ST_AsMVT(mvtgeom.*) FROM mvtgeom
    """
    return db.execute(sql_query).fetchone()[0]
