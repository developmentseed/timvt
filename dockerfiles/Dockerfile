ARG PYTHON_VERSION=3.8

FROM ghcr.io/vincentsarago/uvicorn-gunicorn:${PYTHON_VERSION}

WORKDIR /tmp

COPY README.md README.md
COPY timvt/ timvt/
COPY pyproject.toml pyproject.toml

RUN pip install . --no-cache-dir
RUN rm -rf timvt/ README.md pyproject.toml

ENV MODULE_NAME timvt.main
ENV VARIABLE_NAME app
