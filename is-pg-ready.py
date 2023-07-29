#!/usr/bin/python

import os
import psycopg2

dbname = os.environ.get('POSTGRES_DB')
host = os.environ.get('POSTGRES_HOST')
user = os.environ.get('POSTGRES_USER')
password = os.environ.get('POSTGRES_PASSWORD')

try:
    db = psycopg2.connect(f"dbname='{dbname}' user='{user}' host='{host}' password='{password}'")
except Exception as e:  # pylint: disable=broad-except
    print("Waiting for PostgreSQL to be ready due to exception: %s" % e)
    exit(1)

exit(0)
