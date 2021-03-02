"""test demo endpoints."""


def test_indexjson(app):
    """test /index.json endpoint."""
    response = app.get("/index.json")
    assert response.status_code == 200
    body = response.json()
    print(len(body))
