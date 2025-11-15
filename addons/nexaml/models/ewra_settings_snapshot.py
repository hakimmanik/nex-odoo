# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class EwraSettingsSnapshot(models.Model):
    """Snapshot of EWRA settings at time of assessment."""
    _name = 'nexaml.ewra.settings.snapshot'
    _description = 'EWRA Settings Snapshot'

    run_id = fields.Many2one(
        'nexaml.ewra.run',
        string='EWRA Run',
        required=True,
        ondelete='cascade',
        help='Related EWRA run'
    )

    # Risk Thresholds
    risk_threshold_medium = fields.Float(
        string='Medium Risk Threshold',
        default=1.7,
        help='Score above this is medium risk (default: 1.7)'
    )
    risk_threshold_high = fields.Float(
        string='High Risk Threshold',
        default=2.4,
        help='Score above this is high risk (default: 2.4)'
    )

    # Control Settings
    downgrade_threshold = fields.Integer(
        string='Downgrade Threshold %',
        default=35,
        help='Percentage of low risk required to downgrade (default: 35%)'
    )
    cap_pct = fields.Integer(
        string='Control Cap %',
        default=70,
        help='Maximum control effectiveness (default: 70%)'
    )
    default_control_band = fields.Selection(
        [('weak', 'Weak'),
         ('adequate', 'Adequate'),
         ('strong', 'Strong'),
         ('very_strong', 'Very Strong')],
        string='Default Control Band',
        default='adequate',
        help='Default control effectiveness band'
    )

    # EDD Settings
    edd_threshold = fields.Selection(
        [('medium', 'Medium Risk and Above'),
         ('high', 'High Risk Only')],
        string='EDD Requirement Threshold',
        help='Risk level triggering Enhanced Due Diligence'
    )

    # Screening Settings
    screening_threshold = fields.Float(
        string='Sanctions Match Threshold %',
        help='Minimum match score for sanctions screening'
    )
    auto_screen_on_create = fields.Boolean(
        string='Auto-Screen New Customers',
        help='Automatically screen new partners'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='run_id.company_id',
        store=True,
        help='Company'
    )

    @api.model
    def create_from_current_settings(self, run_id):
        """Create snapshot from current system settings."""
        IrConfigParam = self.env['ir.config_parameter'].sudo()

        return self.create({
            'run_id': run_id,
            'risk_threshold_medium': 1.7,  # Could be configurable
            'risk_threshold_high': 2.4,
            'downgrade_threshold': 35,
            'cap_pct': 70,
            'default_control_band': 'adequate',
            'edd_threshold': IrConfigParam.get_param('nexaml.edd_threshold', 'medium'),
            'screening_threshold': float(IrConfigParam.get_param('nexaml.screening_threshold', '70.0')),
            'auto_screen_on_create': IrConfigParam.get_param('nexaml.auto_screen_on_create', 'False') == 'True',
        })
