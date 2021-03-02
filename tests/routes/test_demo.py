"""test demo endpoints."""


def test_indexjson(app):
    """test /index.json endpoint."""
    response = app.get("/index.json")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == "public.landsat_wrs"
