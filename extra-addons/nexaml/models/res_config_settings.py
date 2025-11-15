# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """AML configuration settings."""
    _inherit = 'res.config.settings'

    # Sanctions Screening Settings
    yente_url = fields.Char(
        string='Screening API URL',
        config_parameter='nexaml.yente_url',
        default='https://sanctions.nex.systems/match/default',
        help='URL of the screening API endpoint for sanctions screening'
    )
    yente_api_key = fields.Char(
        string='Yente API Key',
        config_parameter='nexaml.yente_api_key',
        help='API key for Yente service (if required)'
    )
    screening_threshold = fields.Float(
        string='Match Threshold',
        config_parameter='nexaml.screening_threshold',
        default=70.0,
        help='Minimum match score (0-100) to consider as potential match'
    )
    auto_screen_on_create = fields.Boolean(
        string='Auto-Screen New Customers',
        config_parameter='nexaml.auto_screen_on_create',
        default=False,
        help='Automatically screen partners against sanctions when created'
    )
    screen_related_parties = fields.Boolean(
        string='Screen Related Parties',
        config_parameter='nexaml.screen_related_parties',
        default=True,
        help='Screen directors, shareholders, and UBOs when screening a customer'
    )

    # Risk Assessment Settings
    edd_threshold = fields.Selection(
        [('medium', 'Medium Risk and Above'),
         ('high', 'High Risk Only')],
        string='EDD Requirement',
        config_parameter='nexaml.edd_threshold',
        default='medium',
        help='Risk level that triggers Enhanced Due Diligence requirement'
    )

    # Transaction Monitoring Settings (for future use)
    monitor_invoices = fields.Boolean(
        string='Monitor Invoices',
        config_parameter='nexaml.monitor_invoices',
        default=True,
        help='Enable transaction monitoring for customer invoices'
    )
    monitor_payments = fields.Boolean(
        string='Monitor Payments',
        config_parameter='nexaml.monitor_payments',
        default=True,
        help='Enable transaction monitoring for payments'
    )
