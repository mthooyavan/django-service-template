#!/bin/bash
set -e

# Adjust ownership of the data directory at startup
chown -R postgres:postgres /var/lib/postgresql/data

# PostgreSQL data directory
DATA_DIR="/var/lib/postgresql/data"

# Determine PostgreSQL binary directory
PG_BIN_DIR=$(su - postgres -c "pg_config --bindir")

run_as_postgres() {
    su - postgres -c "$1"
}

# Wait for master to become available, then run the base backup
until PGPASSWORD=$POSTGRES_PASSWORD psql -h db-master -U $POSTGRES_USER -d $POSTGRES_DB -c '\l'; do
    echo 'Waiting for master to become available...'
    sleep 5
done

# If data directory is not initialized, do a base backup from master
if [ ! -s "$DATA_DIR/PG_VERSION" ]; then
    PGPASSWORD=$POSTGRES_PASSWORD pg_basebackup -h db-master -D $DATA_DIR -U $POSTGRES_USER -vP --wal-method=stream
fi

# Create standby.signal file to indicate that this should run as a standby
touch $DATA_DIR/standby.signal

# Append replication settings to postgresql.conf
echo "primary_conninfo = 'host=db-master port=5432 user=$POSTGRES_USER password=$POSTGRES_PASSWORD'" >> $DATA_DIR/postgresql.conf

# Fix data directory permissions
chown -R postgres:postgres "$DATA_DIR" && chmod 0700 "$DATA_DIR"

# Start PostgreSQL in replication mode as the postgres user
run_as_postgres "$PG_BIN_DIR/postgres -D $DATA_DIR -c wal_level=replica -c hot_standby=on -c max_wal_senders=8 -c wal_keep_size=128MB"
