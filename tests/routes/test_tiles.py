"""Test Tiles endpoints."""

import mapbox_vector_tile


def test_index(app):
    """Test /Index."""
    response = app.get("/index")
    assert response.status_code == 200

    resp_json = response.json()
    layer = resp_json[0]

    assert layer["id"] == f"{layer['schema']}.landsat_wrs"
    assert layer["properties"] == {
        "id": "varchar",
        "pr": "varchar",
        "row": "int4",
        "geom": "geometry",
        "path": "int4",
        "ogc_fid": "int4",
    }


def test_tilejson(app):
    """Test TileJSON endpoint."""
    response = app.get("/landsat_wrs.json")
    assert response.status_code == 200

    resp_json = response.json()
    assert resp_json["name"] == "public.landsat_wrs"
    assert resp_json["minzoom"] == 0
    assert resp_json["maxzoom"] == 24
    assert resp_json["bounds"] == [-180, -90, 180, 90]


def test_tile(app):
    """request a tile."""
    response = app.get("/tiles/landsat_wrs/0/0/0.pbf")
    assert response.status_code == 200

    decoded = mapbox_vector_tile.decode(response.content)
    assert len(decoded["default"]["features"]) == 10000
