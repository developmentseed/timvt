#!/bin/sh
# wait-and-start.sh
# waits until database is ready before starting up the app
set -e

until PGPASSWORD=$POSTGRES_PASSWORD PGHOST=$POSTGRES_HOST PGDATABASE=$POSTGRES_DB PGUSER=$POSTGRES_USER pg_isready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
uvicorn timvt.app:app --host=${APP_HOST} --port=${APP_PORT} ${RELOAD:+--reload}
