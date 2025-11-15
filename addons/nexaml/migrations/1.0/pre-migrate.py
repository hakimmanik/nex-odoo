# -*- coding: utf-8 -*-
# Pre-migration script to clean up data before field type changes

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Pre-migration: Fix data incompatibilities before module upgrade."""
    _logger.info("Running pre-migration for nexaml module...")

    # Check if any boolean fields have 'all' value and fix them
    # This can happen if a field was changed from Selection to Boolean

    tables_to_check = [
        ('nexaml_ewra_wizard', 'include_supplier_pillar'),
        ('nexaml_ewra_settings', 'auto_screen_on_create'),
        ('nexaml_ewra_settings_snapshot', 'auto_screen_on_create'),
    ]

    for table, column in tables_to_check:
        try:
            # Check if table and column exist
            cr.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name=%s AND column_name=%s
            """, (table, column))

            result = cr.fetchone()
            if result:
                data_type = result[1]
                _logger.info(f"Found column {table}.{column} with type {data_type}")

                # If it's a varchar/text column with 'all' value, convert to boolean
                if data_type in ('character varying', 'text'):
                    _logger.info(f"Converting {table}.{column} from {data_type} to boolean compatible values")
                    cr.execute(f"""
                        UPDATE {table}
                        SET {column} = CASE
                            WHEN {column} = 'all' THEN 'true'
                            WHEN {column} = 'true' THEN 'true'
                            WHEN {column} = 't' THEN 'true'
                            WHEN {column} = '1' THEN 'true'
                            ELSE 'false'
                        END
                        WHERE {column} IS NOT NULL
                    """)
                    _logger.info(f"Fixed {cr.rowcount} rows in {table}.{column}")
        except Exception as e:
            _logger.warning(f"Could not check/fix {table}.{column}: {e}")

    _logger.info("Pre-migration completed.")
