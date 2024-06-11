#!/usr/bin/python

import os

import psycopg2

dbname = os.environ.get("POSTGRES_DB", "dashboard_dev")
user = os.environ.get("POSTGRES_USER", "dev")
password = os.environ.get("POSTGRES_PASSWORD", "dev")
primary_host = os.environ.get("PRIMARY_POSTGRES_HOST", "localhost")
secondary_host = os.environ.get("SECONDARY_POSTGRES_HOST", None)

try:
    db = psycopg2.connect(
        f"user='{user}' host='{primary_host}' password='{password}' dbname='postgres'"
    )
    db.autocommit = True
    # Check if the database exists and if not, create it
    cursor = db.cursor()
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{dbname}'")
    if not cursor.fetchone():
        cursor.execute(f"CREATE DATABASE {dbname}")
    db.close()
except Exception as exc:  # pylint: disable=broad-except
    print("Waiting for primary PostgreSQL to be ready due to exception: %s" % exc)
    exit(1)

if secondary_host:
    try:
        db = psycopg2.connect(
            f"dbname='{dbname}' user='{user}' host='{secondary_host}' password='{password}'"
        )
        db.close()
    except Exception as exc:  # pylint: disable=broad-except
        print("Waiting for secondary PostgreSQL to be ready due to exception: %s" % exc)
        exit(1)

exit(0)
