# timvt

Create MVT from PostGres

[![CircleCI](https://circleci.com/gh/developmentseed/timvt.svg?style=svg)](https://circleci.com/gh/developmentseed/timvt)
[![codecov](https://codecov.io/gh/developmentseed/timvt/branch/master/graph/badge.svg)](https://codecov.io/gh/developmentseed/timvt)

Timvt, pronounced **tee-tmvtiler** (*ti* is the diminutiveversion of the french *petit* which means small), is lightweight service, which sole goal is to create map tiles dynamically from PG.

Built on top of the *modern and fast* [FastAPI](https://fastapi.tiangolo.com) framework, titiler is written using async/await asynchronous code to improve the performances and handle heavy loads.

### Test locally
```bash
$ git clone https://github.com/developmentseed/timvt.git

$ docker-compose build
$ docker-compose up 
```

## Contribution & Development

Issues and pull requests are more than welcome.

**dev install**

```bash
$ git clone https://github.com/developmentseed/timvt.git
$ cd timvt
$ pip install -e .[dev]
```

**Python3.7 only**

This repo is set to use `pre-commit` to run *my-py*, *flake8*, *pydocstring* and *black* ("uncompromising Python code formatter") when commiting new code.

```bash
$ pre-commit install
```

## Authors
Created by [Development Seed](<http://developmentseed.org>)

