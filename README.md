# TiVTiler

**Work In Progress**

Create Vector Tiles from PostGres

[![CircleCI](https://circleci.com/gh/developmentseed/timvt.svg?style=svg)](https://circleci.com/gh/developmentseed/timvt)
[![codecov](https://codecov.io/gh/developmentseed/timvt/branch/master/graph/badge.svg)](https://codecov.io/gh/developmentseed/timvt)

TiVTiler, pronounced **tee-VTiler** (*ti* is the diminutive version of the french *petit* which means small), is lightweight service, which sole goal is to create Vector Tiles dynamically from Postgres.

Built on top of the *modern and fast* [FastAPI](https://fastapi.tiangolo.com) framework, titiler is written using async/await asynchronous code to improve the performances and handle heavy loads.

## Features

- Multiple TileMatrixSets via [morecantile](https://github.com/developmentseed/morecantile). Default is set to WebMercatorQuad which is the usual Web Mercator projection used in most of Wep Map libraries.)
...

### Test locally
```bash
$ git clone https://github.com/developmentseed/timvt.git

$ docker-compose build
$ docker-compose up 

# Add some data in the db
$ psql -f samples/countries.sql -h localhost -p 5432 -U username -W postgis
```

## Documentation

`:endpoint:/docs`

![](https://user-images.githubusercontent.com/10407788/85869490-be5f0900-b799-11ea-91aa-1d3ff95a46b4.png)


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

