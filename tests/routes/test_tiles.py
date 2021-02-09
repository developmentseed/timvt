"""Test Tiles endpoints."""

import mapbox_vector_tile


def test_tilejson(app):
    """Test TileJSON endpoint."""
    response = app.get("/landsat_wrs.json")
    assert response.status_code == 200

    resp_json = response.json()
    assert resp_json["name"] == "public.landsat_wrs"
    assert resp_json["minzoom"] == 0
    assert resp_json["maxzoom"] == 24
    assert resp_json["bounds"] == [-180.0, -82.6401062011719, 180.0, 82.6401062011719]


def test_tile(app):
    """request a tile."""
    response = app.get("/tiles/landsat_wrs/0/0/0.pbf")
    assert response.status_code == 200

    decoded = mapbox_vector_tile.decode(response.content)
    assert len(decoded["default"]["features"]) == 10000
