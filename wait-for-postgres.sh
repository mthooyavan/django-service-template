#!/usr/bin/env bash
set -e

#waiting for postgres
until python3 is-pg-ready.py
do
  sleep 1
done

echo "DB is up and running"

exec "$@"
