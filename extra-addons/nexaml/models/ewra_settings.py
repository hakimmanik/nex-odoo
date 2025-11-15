# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class EwraSettings(models.Model):
    """Global EWRA Settings Configuration."""
    _name = 'nexaml.ewra.settings'
    _description = 'EWRA Settings'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        help='Company these settings apply to'
    )

    # Risk Thresholds
    risk_threshold_medium = fields.Float(
        string='Medium Threshold',
        default=1.7,
        required=True,
        help='Score at or above this is medium risk (default: 1.7)'
    )
    risk_threshold_high = fields.Float(
        string='High Threshold',
        default=2.4,
        required=True,
        help='Score at or above this is high risk (default: 2.4)'
    )

    # Control Settings
    downgrade_threshold = fields.Integer(
        string='Downgrade %',
        default=35,
        required=True,
        help='If controls are below this %, residual risk equals inherent risk (default: 35%)'
    )
    cap_pct = fields.Integer(
        string='Cap %',
        default=70,
        required=True,
        help='Maximum allowed control effectiveness percentage (default: 70%)'
    )
    default_control_band = fields.Selection(
        [('weak', 'Weak (30%)'),
         ('adequate', 'Adequate (60%)'),
         ('strong', 'Strong (80%)'),
         ('very_strong', 'Very Strong (90%)')],
        string='Default Band',
        default='adequate',
        required=True,
        help='Default control effectiveness band for new EWRA assessments'
    )

    # EDD Settings
    edd_threshold = fields.Selection(
        [('medium', 'Medium Risk and Above'),
         ('high', 'High Risk Only')],
        string='EDD Requirement Threshold',
        default='medium',
        required=True,
        help='Risk level that triggers Enhanced Due Diligence requirements'
    )

    # Screening Settings
    sanctions_match_threshold = fields.Float(
        string='Match Threshold %',
        default=70.0,
        required=True,
        help='Minimum match score % for sanctions screening (default: 70%)'
    )
    auto_screen_on_create = fields.Boolean(
        string='Auto-Screen New',
        default=True,
        help='Automatically screen new partners for sanctions when created'
    )
    screening_frequency_days = fields.Integer(
        string='Frequency (Days)',
        default=90,
        help='How often to re-screen existing customers (default: 90 days)'
    )

    # Pillar Weights
    pillar_weight_customer = fields.Float(
        string='Customer %',
        default=30.0,
        help='Weight of customer risk pillar (default: 30%)'
    )
    pillar_weight_geography = fields.Float(
        string='Geography %',
        default=20.0,
        help='Weight of geography risk pillar (default: 20%)'
    )
    pillar_weight_products = fields.Float(
        string='Products %',
        default=30.0,
        help='Weight of products risk pillar (default: 30%)'
    )
    pillar_weight_delivery = fields.Float(
        string='Delivery %',
        default=20.0,
        help='Weight of delivery channel risk pillar (default: 20%)'
    )

    # Pillar Toggles
    include_customer_pillar = fields.Boolean(
        string='Customer',
        default=True,
        help='Include customer risk in EWRA assessment'
    )
    include_geography_pillar = fields.Boolean(
        string='Geography',
        default=True,
        help='Include geography risk in EWRA assessment'
    )
    include_products_pillar = fields.Boolean(
        string='Products/Services',
        default=True,
        help='Include products/services risk in EWRA assessment'
    )
    include_delivery_pillar = fields.Boolean(
        string='Delivery Channel',
        default=True,
        help='Include delivery channel risk in EWRA assessment'
    )
    supplier_enabled = fields.Boolean(
        string='Supplier',
        default=False,
        help='Enable supplier risk pillar in EWRA assessment'
    )

    # Report & Workflow Settings
    auto_generate_narrative = fields.Boolean(
        string='Auto-Generate Narrative',
        default=True,
        help='Automatically generate narrative using AI after EWRA completion'
    )
    enable_email_notifications = fields.Boolean(
        string='Email Notifications',
        default=False,
        help='Send email notifications for EWRA status changes'
    )
    require_review = fields.Boolean(
        string='Require Review',
        default=False,
        help='Require management review before marking EWRA as complete'
    )

    # Documentation
    methodology_notes = fields.Html(
        string='Methodology Documentation',
        help='Detailed explanation of your organization\'s EWRA methodology'
    )

    _sql_constraints = [
        ('company_unique', 'UNIQUE(company_id)',
         'Only one EWRA settings record allowed per company!')
    ]

    @api.constrains('risk_threshold_medium', 'risk_threshold_high')
    def _check_risk_thresholds(self):
        """Validate risk thresholds are in correct order."""
        for settings in self:
            if settings.risk_threshold_medium >= settings.risk_threshold_high:
                raise ValidationError(
                    _('Medium risk threshold must be less than high risk threshold.')
                )
            if settings.risk_threshold_medium < 1.0 or settings.risk_threshold_high > 3.0:
                raise ValidationError(
                    _('Risk thresholds must be between 1.0 and 3.0.')
                )

    @api.constrains('downgrade_threshold', 'cap_pct')
    def _check_control_percentages(self):
        """Validate control percentages."""
        for settings in self:
            if settings.downgrade_threshold < 0 or settings.downgrade_threshold > 100:
                raise ValidationError(
                    _('Downgrade threshold must be between 0% and 100%.')
                )
            if settings.cap_pct < 0 or settings.cap_pct > 100:
                raise ValidationError(
                    _('Control cap must be between 0% and 100%.')
                )
            if settings.downgrade_threshold > settings.cap_pct:
                raise ValidationError(
                    _('Downgrade threshold cannot exceed control effectiveness cap.')
                )

    @api.constrains('pillar_weight_customer', 'pillar_weight_geography',
                    'pillar_weight_products', 'pillar_weight_delivery')
    def _check_pillar_weights(self):
        """Validate pillar weights sum to 100%."""
        for settings in self:
            total = (settings.pillar_weight_customer +
                     settings.pillar_weight_geography +
                     settings.pillar_weight_products +
                     settings.pillar_weight_delivery)
            if abs(total - 100.0) > 0.01:  # Allow small rounding errors
                raise ValidationError(
                    _('Pillar weights must sum to 100%. Current total: %.1f%%') % total
                )

    @api.model
    def get_settings(self, company_id=None):
        """Get EWRA settings for company, create defaults if not exists."""
        if not company_id:
            company_id = self.env.company.id

        settings = self.search([('company_id', '=', company_id)], limit=1)
        if not settings:
            settings = self.create({'company_id': company_id})

        return settings

    def action_open_methodology(self):
        """Open methodology documentation page."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('EWRA Methodology'),
            'res_model': 'nexaml.ewra.settings',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('nexaml.view_ewra_settings_methodology_form').id,
            'target': 'current',
        }
