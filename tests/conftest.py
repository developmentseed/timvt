"""``pytest`` configuration."""

import pytest

from starlette.testclient import TestClient


@pytest.fixture(autouse=True)
def app(monkeypatch) -> TestClient:
    """Make sure we use monkeypatch env."""
    monkeypatch.setenv("POSTGRES_USER", "jqt")
    monkeypatch.setenv("POSTGRES_PASS", "rde")
    monkeypatch.setenv("POSTGRES_DBNAME", "lobster")
    monkeypatch.setenv("POSTGRES_HOST", "1.2.3.4")
    monkeypatch.setenv("POSTGRES_PORT", "1234")

    from timvt.app import app

    return TestClient(app)
