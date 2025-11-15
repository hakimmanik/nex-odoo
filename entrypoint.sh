#!/bin/bash
set -e

# Wait for postgres to be ready
until PGPASSWORD="$PASSWORD" psql -h "$HOST" -p "$DB_PORT" -U "$USER" -d postgres -c '\q' 2>/dev/null; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - checking database"

# Check if database exists
DB_EXISTS=$(PGPASSWORD="$PASSWORD" psql -h "$HOST" -p "$DB_PORT" -U "$USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='odoo'")

if [ "$DB_EXISTS" != "1" ]; then
  >&2 echo "Database does not exist - initializing with nexaml"
  odoo --init=base,nexaml --database=odoo --db_host="$HOST" --db_user="$USER" --db_password="$PASSWORD" --db_port="$DB_PORT" --stop-after-init --without-demo=all
  >&2 echo "Database initialized successfully"
fi

# Start Odoo
exec odoo "$@"
