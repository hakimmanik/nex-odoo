#!/bin/bash
set -e

# Function to check if database exists
db_exists() {
    PGPASSWORD="$PASSWORD" psql -h "$HOST" -p "$DB_PORT" -U "$USER" -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw odoo
}

# Wait for postgres to be ready
>&2 echo "Waiting for PostgreSQL..."
until PGPASSWORD="$PASSWORD" psql -h "$HOST" -p "$DB_PORT" -U "$USER" -lqt 2>/dev/null; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - checking database"

# Check if database exists and initialize if not
if ! db_exists; then
  >&2 echo "Database 'odoo' does not exist - initializing with nexaml module"
  odoo --init=base,nexaml --database=odoo --db_host="$HOST" --db_user="$USER" --db_password="$PASSWORD" --db_port="$DB_PORT" --stop-after-init --without-demo=all --db_filter=odoo
  >&2 echo "Database initialized successfully"
else
  >&2 echo "Database 'odoo' already exists"
fi

# Start Odoo
>&2 echo "Starting Odoo..."
exec odoo "$@"
