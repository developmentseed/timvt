"""Test timvt.app.app."""


def test_health(app):
    """Test /healthz endpoint."""
    response = app.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"message": "I wear a mask and I wash my hands!"}
