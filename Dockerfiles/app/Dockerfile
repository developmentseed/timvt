FROM tiangolo/uvicorn-gunicorn:python3.8

# Any python libraries that require system libraries to be installed will likely
# need the following packages in order to build
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev

COPY README.md README.md
COPY timvt/ timvt/
COPY setup.py setup.py

RUN pip install -e . --no-cache-dir

ENV MODULE_NAME timvt.main
ENV VARIABLE_NAME app
