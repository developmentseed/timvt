<p align="center">
  <img width="500" src="https://user-images.githubusercontent.com/10407788/172734314-a2b47e51-b919-4aa3-a7cf-33e57f3c2852.png"/>
  <p align="center">A lightweight PostGIS based dynamic vector tile server.</p>
</p>

<p align="center">
  <a href="https://github.com/developmentseed/timvt/actions?query=workflow%3ACI" target="_blank">
      <img src="https://github.com/developmentseed/timvt/workflows/CI/badge.svg" alt="Test">
  </a>
  <a href="https://codecov.io/gh/developmentseed/timvt" target="_blank">
      <img src="https://codecov.io/gh/developmentseed/timvt/branch/master/graph/badge.svg" alt="Coverage">
  </a>
  <a href="https://pypi.org/project/timvt" target="_blank">
      <img src="https://img.shields.io/pypi/v/timvt?color=%2334D058&label=pypi%20package" alt="Package version">
  </a>
  <a href="https://github.com/developmentseed/timvt/blob/master/LICENSE" target="_blank">
      <img src="https://img.shields.io/github/license/developmentseed/timvt.svg" alt="License">

  </a>
</p>

---

**Documentation**: <a href="https://developmentseed.org/timvt/" target="_blank">https://developmentseed.org/timvt/</a>

**Source Code**: <a href="https://github.com/developmentseed/timvt" target="_blank">https://github.com/developmentseed/timvt</a>

---

`TiMVT`, pronounced **tee-MVT**, is a python package which helps creating lightweight [Vector Tiles](https://github.com/mapbox/vector-tile-spec) service from [PostGIS](https://github.com/postgis/postgis) Database.

Built on top of the *modern and fast* [FastAPI](https://fastapi.tiangolo.com) framework, timvt is written in Python using async/await asynchronous code to improve the performances and handle heavy loads.

`TiMVT` is mostly inspired from the awesome [urbica/martin](https://github.com/urbica/martin) and [CrunchyData/pg_tileserv](https://github.com/CrunchyData/pg_tileserv) projects.

## Features

- Multiple TileMatrixSets via [morecantile](https://github.com/developmentseed/morecantile). Default is set to WebMercatorQuad which is the usual Web Mercator projection used in most of Wep Map libraries.)
- Built with [FastAPI](https://fastapi.tiangolo.com)
- Table and Function layers
- Async API using [asyncpg](https://github.com/MagicStack/asyncpg)


## Install

Install `TiMVT` from pypi
```bash
# update pip (optional)
python -m pip install pip -U

# install timvt
python -m pip install timvt
```

or install from source:

```bash
$ git clone https://github.com/developmentseed/timvt.git
$ cd timvt
$ python -m pip install -e .
```

## PostGIS/Postgres

`TiMVT` rely mostly on [`ST_AsMVT`](https://postgis.net/docs/ST_AsMVT.html) function and will need PostGIS >= 2.5.

If you want more info about `ST_AsMVT` function or on the subject of creating Vector Tile from PostGIS, please read this great article from Paul Ramsey: https://info.crunchydata.com/blog/dynamic-vector-tiles-from-postgis

### Configuration

To be able to create Vector Tile, the application will need access to the PostGIS database. `TiMVT` uses [pydantic](https://pydantic-docs.helpmanual.io/usage/settings/)'s configuration pattern which make use of environment variable and/or `.env` file to pass variable to the application.

Example of `.env` file can be found in [.env.example](https://github.com/developmentseed/timvt/blob/master/.env.example)
```
POSTGRES_USER=username
POSTGRES_PASS=password
POSTGRES_DBNAME=postgis
POSTGRES_HOST=0.0.0.0
POSTGRES_PORT=5432

# Or you can also define the DATABASE_URL directly
DATABASE_URL=postgresql://username:password@0.0.0.0:5432/postgis
```

## Minimal Application

```python
from timvt.db import close_db_connection, connect_to_db
from timvt.factory import VectorTilerFactory
from timvt.layer import FunctionRegistry
from fastapi import FastAPI, Request

# Create Application.
app = FastAPI()

# Add Function registry to the application state
app.state.timvt_function_catalog = FunctionRegistry()

# Register Start/Stop application event handler to setup/stop the database connection
# and populate `app.state.table_catalog`
@app.on_event("startup")
async def startup_event():
    """Application startup: register the database connection and create table list."""
    await connect_to_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown: de-register the database connection."""
    await close_db_connection(app)

# Register endpoints.
mvt_tiler = VectorTilerFactory(
    with_tables_metadata=True,
    with_functions_metadata=True,  # add Functions metadata endpoints (/functions.json, /{function_name}.json)
    with_viewer=True,
)
app.include_router(mvt_tiler.router, tags=["Tiles"])
```

## Default Application

While we encourage users to write their own application using `TiMVT` package, we also provide a default `production ready` application:

```bash
# Install timvt dependencies and Uvicorn (a lightning-fast ASGI server)
$ pip install timvt 'uvicorn[standard]>=0.12.0,<0.14.0'

# Set Database URL environment variable so TiMVT can access it
$ export DATABASE_URL=postgresql://username:password@0.0.0.0:5432/postgis

# Launch Demo Application
$ uvicorn timvt.main:app --reload
```

You can also use the official docker image

```
$ docker run \
    -p 8081:8081 \
    -e PORT=8081 \
    -e DATABASE_URL=postgresql://username:password@0.0.0.0:5432/postgis \
    ghcr.io/developmentseed/timvt:latest
```

`:endpoint:/docs`

![](https://user-images.githubusercontent.com/10407788/202146065-2ddcf159-123c-48f9-a208-7dcd46201cb4.png)


## Contribution & Development

See [CONTRIBUTING.md](https://github.com/developmentseed/timvt/blob/master/CONTRIBUTING.md)

## License

See [LICENSE](https://github.com/developmentseed/timvt/blob/master/LICENSE)

## Authors

Created by [Development Seed](<http://developmentseed.org>)

## Changes

See [CHANGES.md](https://github.com/developmentseed/timvt/blob/master/CHANGES.md).

