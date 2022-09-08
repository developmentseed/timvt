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

    func = list(filter(lambda x: x["id"] == "landsat_poly_centroid", body))[0]
    assert func["id"] == "landsat_poly_centroid"
    assert func["function_name"] == "landsat_poly_centroid"
    assert func["bounds"]
    assert func["tileurl"]
    assert "options" not in func

    func = list(filter(lambda x: x["id"] == "squares", body))[0]
    assert func["id"] == "squares"
    assert func["function_name"] == "squares"
    assert func["bounds"]
    assert func["tileurl"]
    assert "options" not in func

    func = list(filter(lambda x: x["id"] == "squares2", body))[0]
    assert func["id"] == "squares2"
    assert func["function_name"] == "squares"
    assert func["bounds"] == [0.0, 0.0, 180.0, 90.0]
    assert func["tileurl"]
    assert func["options"] == [{"name": "depth", "default": 2}]


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
