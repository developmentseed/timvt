"""``pytest`` configuration."""

import os

import pytest
import pytest_pgsql

from starlette.testclient import TestClient

DATA_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


test_db = pytest_pgsql.TransactedPostgreSQLTestDB.create_fixture(
    "test_db", scope="session", use_restore_state=False
)


@pytest.fixture(scope="session")
def database_url(test_db):
    """
    Session scoped fixture to launch a postgresql database in a separate process.  We use psycopg2 to ingest test data
    because pytest-asyncio event loop is a function scoped fixture and cannot be called within the current scope.  Yields
    a database url which we pass to our application through a monkeypatched environment variable.
    """
    assert test_db.install_extension("postgis")
    test_db.run_sql_file(os.path.join(DATA_DIR, "data", "landsat_wrs.sql"))
    assert test_db.has_table("landsat_wrs")
    return test_db.connection.engine.url


@pytest.fixture(autouse=True)
def app(database_url, monkeypatch):
    """Create app with connection to the pytest database."""
    monkeypatch.setenv("DATABASE_URL", str(database_url))
    monkeypatch.setenv("TIMVT_DEFAULT_MINZOOM", str(5))
    monkeypatch.setenv("TIMVT_DEFAULT_MAXZOOM", str(12))
    monkeypatch.setenv("TIMVT_FUNCTIONS_DIRECTORY", DATA_DIR)

    from timvt.layer import Function
    from timvt.main import app

    # Register the same function but we different options
    app.state.timvt_function_catalog.register(
        Function.from_file(
            id="squares2",
            infile=os.path.join(DATA_DIR, "squares.sql"),
            function_name="squares",
            minzoom=0,
            maxzoom=9,
            bounds=[0.0, 0.0, 180.0, 90.0],
            options=[{"name": "depth", "default": 2}],
        )
    )

    with TestClient(app) as app:
        yield app
