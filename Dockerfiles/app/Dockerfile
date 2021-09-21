FROM tiangolo/uvicorn-gunicorn:python3.8

COPY README.md README.md
COPY timvt/ timvt/
COPY setup.py setup.py

RUN pip install . --no-cache-dir

RUN rm -rf timvt/ README.md setup.py

ENV MODULE_NAME timvt.main
ENV VARIABLE_NAME app
