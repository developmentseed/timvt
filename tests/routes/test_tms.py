"""test TileMatrixSets endpoints."""
from urllib.parse import urlsplit

import mapbox_vector_tile


def test_index(app):
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


def test_tilematrix(app):
    """test /tileMatrixSet endpoint."""
    response = app.get("/tileMatrixSets")
    assert response.status_code == 200
    body = response.json()
    assert len(body["tileMatrixSets"]) == 12  # morecantile has 10 defaults
    tms = list(filter(lambda m: m["id"] == "EPSG3413", body["tileMatrixSets"]))[0]
    assert tms["links"][0]["href"] == "http://testserver/tileMatrixSets/EPSG3413"


def test_tilematrixInfo(app):
    """test /tileMatrixSet endpoint."""
    response = app.get("/tileMatrixSets/EPSG3413")
    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "TileMatrixSetType"
    assert body["identifier"] == "EPSG3413"


def test_tilejson(app):
    response = app.get("/landsat_wrs.json")
    assert response.status_code == 200

    resp_json = response.json()
    assert resp_json["name"] == "public.landsat_wrs"
    assert resp_json["minzoom"] == 0
    assert resp_json["maxzoom"] == 24
    assert resp_json["bounds"] == [-180, -90, 180, 90]

    # request a tile
    tile_url = resp_json["tiles"][0].format(x=0, y=0, z=0)
    response = app.get(urlsplit(tile_url).path)
    assert response.status_code == 200

    decoded = mapbox_vector_tile.decode(response.content)
    assert len(decoded["default"]["features"]) == 10000
