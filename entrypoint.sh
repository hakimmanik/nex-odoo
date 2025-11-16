#!/bin/bash
set -e

# Configuration - use environment variables from docker-compose
: ${HOST:=db}
: ${USER:=odoo}
: ${PASSWORD:=odoo}
: ${DB_PORT:=5432}
: ${DB_NAME:=odoo}

# Debug: Check if extra-addons directory exists
echo "=== DEBUG: Checking /mnt/extra-addons directory ==="
if [ -d "/mnt/extra-addons" ]; then
  echo "Directory exists, listing contents:"
  ls -la /mnt/extra-addons
else
  echo "ERROR: /mnt/extra-addons does not exist!"
fi
echo "============================================"

# Set PostgreSQL environment variables for psql
export PGHOST="$HOST"
export PGPORT="$DB_PORT"
export PGUSER="$USER"
export PGPASSWORD="$PASSWORD"

# Wait for postgres to be ready
echo "Waiting for PostgreSQL to be ready..."
until psql -l 2>/dev/null | grep -q template1; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - checking database"

# Check if database exists and is initialized
if psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
  echo "Database '$DB_NAME' exists. Checking if initialized..."

  # Check if ir_module_module table exists (indicates initialized DB)
  if psql -d "$DB_NAME" -tAc "SELECT 1 FROM information_schema.tables WHERE table_name='ir_module_module'" | grep -q 1; then
    echo "Database is initialized."
  else
    echo "Database exists but not initialized. Initializing with nexaml module..."

    # Initialize database with base and nexaml modules
    odoo --init=base,nexaml \
         --database="$DB_NAME" \
         --db_host="$HOST" \
         --db_port="$DB_PORT" \
         --db_user="$USER" \
         --db_password="$PASSWORD" \
         --without-demo=all \
         --stop-after-init

    echo "Database initialized with nexaml module!"
  fi
else
  echo "Database '$DB_NAME' does not exist. Creating and initializing with nexaml module..."

  # Initialize database with base and nexaml modules
  odoo --init=base,nexaml \
       --database="$DB_NAME" \
       --db_host="$HOST" \
       --db_port="$DB_PORT" \
       --db_user="$USER" \
       --db_password="$PASSWORD" \
       --without-demo=all \
       --stop-after-init

  echo "Database initialized with nexaml module!"
fi

# Start Odoo with original arguments
echo "Starting Odoo..."
exec odoo "$@"
