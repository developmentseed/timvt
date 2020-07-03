**Work In Progress**

<p align="center">
  <img src="https://user-images.githubusercontent.com/10407788/85882807-ed7f7580-b7ad-11ea-9f7a-86b989761d79.png"/>
  <p align="center">A lightweight PostGIS based dynamic vector tile server.</p>
</p>

# TiVTiler

[![CircleCI](https://circleci.com/gh/developmentseed/timvt.svg?style=svg)](https://circleci.com/gh/developmentseed/timvt)
[![codecov](https://codecov.io/gh/developmentseed/timvt/branch/master/graph/badge.svg)](https://codecov.io/gh/developmentseed/timvt)

TiVTiler, pronounced **tee-VTiler**, is lightweight service, which sole goal is to create [Vector Tiles](https://github.com/mapbox/vector-tile-spec) dynamically from [PostGIS](https://github.com/postgis/postgis).

Built on top of the *modern and fast* [FastAPI](https://fastapi.tiangolo.com) framework, titiler is written in Python using async/await asynchronous code to improve the performances and handle heavy loads.

TiVTiler is mostly inspired from the awesome [urbica/martin](https://github.com/urbica/martin) and [CrunchyData](https://github.com/CrunchyData/pg_tileserv) projects.

#### Features

- Multiple TileMatrixSets via [morecantile](https://github.com/developmentseed/morecantile). Default is set to WebMercatorQuad which is the usual Web Mercator projection used in most of Wep Map libraries.)
- ...

## Requirements and Setup

#### Python Requirements
- [FastAPI](https://fastapi.tiangolo.com): *Modern, fast (high-performance), web framework for building APIs*
- [Morecantile](https://github.com/developmentseed/morecantile) (Rasterio/GDAL): *Construct and use map tile grids (a.k.a TileMatrixSet / TMS)*
- [asyncpg](https://github.com/MagicStack/asyncpg) *A fast PostgreSQL Database Client Library for Python/asyncio* 


#### PostGIS/Postgres

TiVTiler rely mostly on [`ST_AsMVT`](https://postgis.net/docs/ST_AsMVT.html) function and will need PostGIS >= 2.5. 

If you want more info about `ST_AsMVT` function or on the subject of creating Vector Tile from PostGIS, please read this great article from Paul Ramsey: https://info.crunchydata.com/blog/dynamic-vector-tiles-from-postgis

### Setup locally

1. Download
```
$ git clone https://github.com/developmentseed/timvt.git && cd timvt
```
2. Install
```
# Install TiVTiler dependencies and Uvicorn (a lightning-fast ASGI server)
$ pip install -e .["server"]
```
3. Configuration

To be able to create Vector Tile, the application will need access to the PostGIS database. TiVTiler uses [starlette](https://www.starlette.io/config/)'s configuration pattern which make use of environment variable and/or `.env` file to pass variable to the application.

Example of `.env` file can be found in [.env.example](.env.example)
```
POSTGRES_USER=username
POSTGRES_PASS=password
POSTGRES_DBNAME=postgis
POSTGRES_HOST=0.0.0.0
POSTGRES_PORT=5432
```

4. Launch
```
$ uvicorn timvt.app:app --reload
```

### With Docker

Using Docker is maybe the easiest approach, and with `docker-compose` it's even easier to setup the database and the application using only one command line.

```bash
$ git clone https://github.com/developmentseed/timvt.git
$ docker-compose up --build
```

## Documentation

`:endpoint:/docs`

![](https://user-images.githubusercontent.com/10407788/85869490-be5f0900-b799-11ea-91aa-1d3ff95a46b4.png)



# Project structure

```
demo/                            - Leaflet/Mapbox demo
 │
Dockerfiles/                     - Dockerfiles.
 ├── app/
 │   └── Dockerfile              - TiVTiler Application dockerfile (python:3.8-slim).
 ├── db/
 │   ├── countries.sql           - Natural Earth test dataset.
 │   └── Dockerfile              - PostGIS dockerfile (postgis/postgis:12-3.0).
 │
tests/                           - TiVTiler Python Unitest suite.
 │
timvt/                           - python module.
 ├── endpoints/                  - Application routes.
 │   ├── demo.py                 - Demo web pages.
 │   ├── health.py               - health check endpoint.
 │   ├── index.py                - Table metadata and list.
 │   ├── tiles.py                - Tile related endpoints.
 │   └── tms.py                  - TileMatrixSet list and metadata.
 ├── custom/                     - Custom TMS grids.
 ├── db/                         - db related tools.
 ├── models/                     - pydantic models for this application.
 ├── ressources/                 - application ressources (enums, constants, ...).
 ├── templates/                  - factory and html templates.
 ├── utils/                      - application tools (dependencies, timer, ...).
 ├── main.py                     - FastAPI application creation and configuration.
 └── utils.py                    - utility functions.
 
```


# Contribution & Development

Issues and pull requests are more than welcome.

**dev install**

```bash
$ git clone https://github.com/developmentseed/timvt.git
$ cd titiler
$ pip install -e .[dev]
```

**Python3.7 only**

This repo is set to use `pre-commit` to run *isort*, *mypy*, *flake8*, *pydocstring* and *black* ("uncompromising Python code formatter") when commiting new code.

```bash
$ pre-commit install
```

## Authors
Created by [Development Seed](<http://developmentseed.org>)

