FROM python:3.8-slim

# Any python libraries that require system libraries to be installed will likely
# need the following packages in order to build
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    git

COPY README.md /app/README.md
COPY timvt/ /app/timvt/
COPY setup.py /app/setup.py
COPY Dockerfiles/app/wait-and-start.sh /app/

RUN pip install -e /app/.["server"] --no-cache-dir

ENV APP_HOST=0.0.0.0
ENV APP_PORT=80

ENV RELOAD=''

CMD uvicorn timvt.app:app --host=${APP_HOST} --port=${APP_PORT} ${RELOAD:+--reload}
