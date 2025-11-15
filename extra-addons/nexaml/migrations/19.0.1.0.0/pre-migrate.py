# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

"""Pre-migration script to rename aml_risk_score to risk_score."""

import logging
from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _column_exists(cr, table, column):
    """Check if a column exists in a table."""
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name=%s AND column_name=%s
    """, (table, column))
    return bool(cr.fetchone())


def migrate(cr, version):
    """Rename aml_risk_score to risk_score in product_template and account_payment_method."""
    _logger.info("Running NexAML pre-migration: renaming aml_risk_score to risk_score")

    # Rename column in product_template
    if _column_exists(cr, 'product_template', 'aml_risk_score'):
        if not _column_exists(cr, 'product_template', 'risk_score'):
            _logger.info("Renaming product_template.aml_risk_score to risk_score")
            cr.execute("""
                ALTER TABLE product_template
                RENAME COLUMN aml_risk_score TO risk_score
            """)
        else:
            _logger.warning("Column product_template.risk_score already exists, skipping rename")

    # Rename column in account_payment_method
    if _column_exists(cr, 'account_payment_method', 'aml_risk_score'):
        if not _column_exists(cr, 'account_payment_method', 'risk_score'):
            _logger.info("Renaming account_payment_method.aml_risk_score to risk_score")
            cr.execute("""
                ALTER TABLE account_payment_method
                RENAME COLUMN aml_risk_score TO risk_score
            """)
        else:
            _logger.warning("Column account_payment_method.risk_score already exists, skipping rename")

    _logger.info("NexAML pre-migration completed successfully")
