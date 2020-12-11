"""``pytest`` configuration."""

import os
import tempfile

import psycopg2
import pytest
from pytest_postgresql import factories

from starlette.testclient import TestClient

DATA_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


# Create a temporary postgresql instance for the test session, running on :5432
postgresql_port = 5432
socket_dir = tempfile.TemporaryDirectory()
postgresql_my_proc = factories.postgresql_proc(
    unixsocketdir=socket_dir.name, port=postgresql_port,
)


@pytest.fixture(scope="session")
def database_url(postgresql_my_proc):
    """
    Session scoped fixture to launch a postgresql database in a separate process.  We use psycopg2 to ingest test data
    because pytest-asyncio event loop is a function scoped fixture and cannot be called within the current scope.  Yields
    a database url which we pass to our application through a monkeypatched environment variable.
    """
    db_url = f"postgresql://{postgresql_my_proc.user}:{postgresql_my_proc.password}@{postgresql_my_proc.host}:{postgresql_port}"
    conn = psycopg2.connect(dsn=db_url)
    cursor = conn.cursor()
    cursor.execute("CREATE EXTENSION postgis")
    cursor.execute(open(os.path.join(DATA_DIR, "landsat_wrs.sql")).read())
    yield db_url
    conn.close()


@pytest.fixture
def app(database_url, monkeypatch):
    """Create app with connection to the pytest database."""
    monkeypatch.setenv("DATABASE_URL", database_url)

    from timvt.app import app

    with TestClient(app) as app:
        yield app
