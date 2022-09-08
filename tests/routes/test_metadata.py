"""test demo endpoints."""

import numpy as np


def test_table_index(app):
    """test /tables.json endpoint."""
    response = app.get("/tables.json")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == "public.landsat_wrs"
    assert body[0]["bounds"]
    assert body[0]["tileurl"]


def test_table_info(app):
    """Test metadata endpoint."""
    response = app.get("/table/public.landsat_wrs.json")
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json["id"] == "public.landsat_wrs"
    assert resp_json["minzoom"] == 5
    assert resp_json["maxzoom"] == 12
    assert resp_json["tileurl"]

    np.testing.assert_almost_equal(
        resp_json["bounds"], [-180.0, -82.6401062011719, 180.0, 82.6401062011719]
    )


def test_function_index(app):
    """test /functions.json endpoint."""
    response = app.get("/functions.json")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3

    assert body[0]["id"] == "landsat_poly_centroid"
    assert body[0]["function_name"] == "landsat_poly_centroid"
    assert body[0]["bounds"]
    assert body[0]["tileurl"]
    assert "options" not in body[0]

    assert body[1]["id"] == "squares"
    assert body[1]["function_name"] == "squares"
    assert body[1]["bounds"]
    assert body[1]["tileurl"]
    assert "options" not in body[1]

    assert body[2]["id"] == "squares2"
    assert body[2]["function_name"] == "squares"
    assert body[2]["bounds"] == [0.0, 0.0, 180.0, 90.0]
    assert body[2]["tileurl"]
    assert body[2]["options"] == [{"name": "depth", "default": 2}]


def test_function_info(app):
    """Test metadata endpoint."""
    response = app.get("/function/squares.json")
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json["id"] == "squares"
    assert resp_json["function_name"] == "squares"
    assert resp_json["minzoom"] == 5
    assert resp_json["maxzoom"] == 12
    assert resp_json["tileurl"]
    assert "options" not in resp_json
    np.testing.assert_almost_equal(resp_json["bounds"], [-180, -90, 180, 90])

    response = app.get("/function/squares2.json")
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json["id"] == "squares2"
    assert resp_json["function_name"] == "squares"
    assert resp_json["minzoom"] == 0
    assert resp_json["maxzoom"] == 9
    assert resp_json["tileurl"]
    assert resp_json["options"] == [{"name": "depth", "default": 2}]
    np.testing.assert_almost_equal(resp_json["bounds"], [0.0, 0.0, 180.0, 90.0])
