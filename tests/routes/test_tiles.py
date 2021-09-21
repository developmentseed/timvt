"""Test Tiles endpoints."""

import mapbox_vector_tile
import numpy as np


def test_tilejson(app):
    """Test TileJSON endpoint."""
    response = app.get("/public.landsat_wrs/tilejson.json")
    assert response.status_code == 200

    resp_json = response.json()
    assert resp_json["name"] == "public.landsat_wrs"
    assert resp_json["minzoom"] == 5
    assert resp_json["maxzoom"] == 12

    np.testing.assert_almost_equal(
        resp_json["bounds"], [-180.0, -82.6401062011719, 180.0, 82.6401062011719]
    )

    response = app.get("/public.landsat_wrs/tilejson.json?minzoom=1&maxzoom=2")
    assert response.status_code == 200

    resp_json = response.json()
    assert resp_json["name"] == "public.landsat_wrs"
    assert resp_json["minzoom"] == 1
    assert resp_json["maxzoom"] == 2

    response = app.get(
        "/public.landsat_wrs/tilejson.json?minzoom=1&maxzoom=2&limit=1000"
    )
    assert response.status_code == 200

    resp_json = response.json()
    assert resp_json["name"] == "public.landsat_wrs"
    assert resp_json["minzoom"] == 1
    assert resp_json["maxzoom"] == 2
    assert "?limit=1000" in resp_json["tiles"][0]


def test_tile(app):
    """request a tile."""
    response = app.get("/tiles/public.landsat_wrs/0/0/0.pbf")
    assert response.status_code == 200

    decoded = mapbox_vector_tile.decode(response.content)
    assert len(decoded["default"]["features"]) == 10000

    response = app.get("/tiles/public.landsat_wrs/0/0/0.pbf?limit=1000")
    assert response.status_code == 200

    decoded = mapbox_vector_tile.decode(response.content)
    assert len(decoded["default"]["features"]) == 1000
