#!/bin/bash
set -e

# Adjust ownership of the data directory at startup
chown -R postgres:postgres /var/lib/postgresql/data

# PostgreSQL data directory
DATA_DIR="/var/lib/postgresql/data"

# Determine PostgreSQL binary directory
PG_BIN_DIR=$(su - postgres -c "pg_config --bindir")

# Function to run commands as the postgres user
run_as_postgres() {
    su - postgres -c "$1"
}

# Debug: Print environment variables
echo "DEBUG: POSTGRES_USER is $POSTGRES_USER"
echo "DEBUG: POSTGRES_PASSWORD is [hidden for security]"

# Check if PostgreSQL has been initialized
if [ ! -s "$DATA_DIR/PG_VERSION" ]; then
    # The directory is empty or doesn't contain the PG_VERSION file, indicating a fresh installation
    echo "Initializing PostgreSQL Database..."

    # Initialize PostgreSQL as postgres user
    run_as_postgres "$PG_BIN_DIR/initdb -D $DATA_DIR"

    # Set PostgreSQL configurations
    echo "host replication $POSTGRES_USER 0.0.0.0/0 trust" >> "$DATA_DIR/pg_hba.conf"
    echo "host all $POSTGRES_USER 0.0.0.0/0 trust" >> "$DATA_DIR/pg_hba.conf"
    echo "listen_addresses='*'" >> "$DATA_DIR/postgresql.conf"

    # Start PostgreSQL in the background to set up the user and replication permissions
    run_as_postgres "$PG_BIN_DIR/pg_ctl -D $DATA_DIR -o '-c listen_addresses=localhost' -w start"

    # Create the POSTGRES_USER if it doesn't exist (simplified for debugging)
    run_as_postgres "$PG_BIN_DIR/psql -v ON_ERROR_STOP=0 --username postgres -c 'CREATE USER \"$POSTGRES_USER\" WITH SUPERUSER PASSWORD '\''$POSTGRES_PASSWORD'\'';'"

    # Create the POSTGRES_DB if it doesn't exist (simplified for debugging)
    run_as_postgres "$PG_BIN_DIR/psql -v ON_ERROR_STOP=0 --username postgres -c 'CREATE DATABASE \"$POSTGRES_DB\" OWNER \"$POSTGRES_USER\";'"

    # Create the DASHBOARD_DB if it doesn't exist (simplified for debugging)
    run_as_postgres "$PG_BIN_DIR/psql -v ON_ERROR_STOP=0 --username postgres -c 'CREATE DATABASE \"$DASHBOARD_DB\" OWNER \"$POSTGRES_USER\";'"

    # Ensure POSTGRES_USER has replication permissions
    run_as_postgres "$PG_BIN_DIR/psql -v ON_ERROR_STOP=1 --username $POSTGRES_USER --dbname $POSTGRES_DB -c 'ALTER USER \"$POSTGRES_USER\" WITH REPLICATION;'"
    run_as_postgres "$PG_BIN_DIR/psql -v ON_ERROR_STOP=1 --username $POSTGRES_USER --dbname $DASHBOARD_DB -c 'ALTER USER \"$POSTGRES_USER\" WITH REPLICATION;'"

    # Stop the temporary PostgreSQL instance
    run_as_postgres "$PG_BIN_DIR/pg_ctl -D $DATA_DIR -m fast -w stop"
fi

# Start PostgreSQL with user-defined configurations as postgres user
run_as_postgres "$PG_BIN_DIR/postgres -D $DATA_DIR -c wal_level=replica -c max_wal_senders=8 -c wal_keep_size=128MB"
