"""test demo endpoints."""

import numpy as np


def test_indexjson(app):
    """test /index.json endpoint."""
    response = app.get("/index.json")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == "public.landsat_wrs"
    assert body[0]["bounds"]


def test_info(app):
    """Test metadata endpoint."""
    response = app.get("/public.landsat_wrs.json")
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json["id"] == "public.landsat_wrs"
    assert resp_json["minzoom"] == 5
    assert resp_json["maxzoom"] == 12

    np.testing.assert_almost_equal(
        resp_json["bounds"], [-180.0, -82.6401062011719, 180.0, 82.6401062011719]
    )
