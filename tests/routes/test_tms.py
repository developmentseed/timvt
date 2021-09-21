"""test TileMatrixSets endpoints."""


def test_tilematrix(app):
    """test /tileMatrixSet endpoint."""
    response = app.get("/tileMatrixSets")
    assert response.status_code == 200
    body = response.json()

    assert len(body["tileMatrixSets"]) == 11  # morecantile has 10 defaults
    tms = list(filter(lambda m: m["id"] == "WebMercatorQuad", body["tileMatrixSets"]))[
        0
    ]
    assert tms["links"][0]["href"] == "http://testserver/tileMatrixSets/WebMercatorQuad"


def test_tilematrixInfo(app):
    """test /tileMatrixSet endpoint."""
    response = app.get("/tileMatrixSets/WebMercatorQuad")
    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "TileMatrixSetType"
    assert body["identifier"] == "WebMercatorQuad"
