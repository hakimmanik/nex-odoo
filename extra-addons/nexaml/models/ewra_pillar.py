# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class EwraPillar(models.Model):
    """EWRA Risk Pillar Assessment."""
    _name = 'nexaml.ewra.pillar'
    _description = 'EWRA Risk Pillar'
    _order = 'sequence, id'

    run_id = fields.Many2one(
        'nexaml.ewra.run',
        string='EWRA Run',
        required=True,
        ondelete='cascade',
        help='Related EWRA run'
    )
    pillar = fields.Selection(
        [('customer', 'Customer Risk'),
         ('geography', 'Geography Risk'),
         ('products', 'Products & Services Risk'),
         ('delivery', 'Delivery Channel Risk'),
         ('supplier', 'Supplier Risk')],
        string='Risk Pillar',
        required=True,
        help='Type of risk pillar'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Display order'
    )

    # Risk Distribution
    low_pct = fields.Float(
        string='Low Risk %',
        help='Percentage of entities classified as low risk (0-100)'
    )
    medium_pct = fields.Float(
        string='Medium Risk %',
        help='Percentage of entities classified as medium risk (0-100)'
    )
    high_pct = fields.Float(
        string='High Risk %',
        help='Percentage of entities classified as high risk (0-100)'
    )

    # Inherent Risk
    inherent_score = fields.Float(
        string='Inherent Risk Score',
        compute='_compute_inherent_score',
        store=True,
        help='Calculated inherent risk score (1.0-3.0)'
    )
    inherent_label = fields.Selection(
        [('low', 'Low'),
         ('medium', 'Medium'),
         ('high', 'High')],
        string='Inherent Risk Level',
        compute='_compute_inherent_label',
        store=True,
        help='Inherent risk classification'
    )

    # Controls
    control_pct = fields.Float(
        string='Control Effectiveness %',
        compute='_compute_effective_control_pct',
        store=True,
        help='Control effectiveness percentage (0-70%)'
    )
    control_band = fields.Selection(
        [('weak', 'Weak (0-20%)'),
         ('adequate', 'Adequate (21-40%)'),
         ('strong', 'Strong (41-55%)'),
         ('very_strong', 'Very Strong (56-70%)'),
         ('custom', 'Custom')],
        string='Control Band',
        default='adequate',
        help='Control effectiveness classification'
    )
    custom_control_pct = fields.Float(
        string='Custom Control %',
        help='Custom control effectiveness percentage when band is "custom" (0-70%)'
    )
    control_reason = fields.Char(
        string='Control Justification',
        help='Reason for the chosen control effectiveness level'
    )

    # Residual Risk
    residual_score = fields.Float(
        string='Residual Risk Score',
        compute='_compute_residual_score',
        store=True,
        help='Risk score after controls (1.0-3.0)'
    )
    residual_label = fields.Selection(
        [('low', 'Low'),
         ('medium', 'Medium'),
         ('high', 'High')],
        string='Residual Risk Level',
        compute='_compute_residual_label',
        store=True,
        help='Residual risk classification'
    )

    # Notes
    notes = fields.Html(
        string='Assessment Notes',
        help='Detailed notes about this pillar assessment'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='run_id.company_id',
        store=True,
        help='Company'
    )

    @api.depends('low_pct', 'medium_pct', 'high_pct')
    def _compute_inherent_score(self):
        """Calculate inherent risk score from distribution.
        Formula: (Low% × 1.0) + (Medium% × 2.0) + (High% × 3.0) / 100
        """
        for pillar in self:
            low = pillar.low_pct or 0.0
            medium = pillar.medium_pct or 0.0
            high = pillar.high_pct or 0.0

            pillar.inherent_score = ((low * 1.0) + (medium * 2.0) + (high * 3.0)) / 100.0

    @api.depends('inherent_score')
    def _compute_inherent_label(self):
        """Classify inherent risk level."""
        for pillar in self:
            score = pillar.inherent_score
            if score < 1.7:
                pillar.inherent_label = 'low'
            elif score < 2.4:
                pillar.inherent_label = 'medium'
            else:
                pillar.inherent_label = 'high'

    @api.depends('control_band', 'custom_control_pct')
    def _compute_effective_control_pct(self):
        """Get effective control percentage based on band or custom value."""
        for pillar in self:
            if pillar.control_band == 'custom':
                pillar.control_pct = pillar.custom_control_pct or 0.0
            elif pillar.control_band == 'weak':
                pillar.control_pct = 30.0
            elif pillar.control_band == 'adequate':
                pillar.control_pct = 60.0
            elif pillar.control_band == 'strong':
                pillar.control_pct = 80.0
            elif pillar.control_band == 'very_strong':
                pillar.control_pct = 90.0
            else:
                pillar.control_pct = 0.0

    @api.depends('inherent_score', 'control_pct', 'control_band', 'custom_control_pct')
    def _compute_residual_score(self):
        """Calculate residual risk after applying controls.
        Formula: Inherent Score × (1 - Control% / 100)
        """
        for pillar in self:
            # Get effective control percentage
            if pillar.control_band == 'custom':
                control_pct = pillar.custom_control_pct or 0.0
            else:
                control_pct = pillar.control_pct or 0.0

            inherent = pillar.inherent_score
            control = control_pct / 100.0
            pillar.residual_score = max(1.0, inherent * (1 - control))

    @api.depends('residual_score')
    def _compute_residual_label(self):
        """Classify residual risk level."""
        for pillar in self:
            score = pillar.residual_score
            if score < 1.7:
                pillar.residual_label = 'low'
            elif score < 2.4:
                pillar.residual_label = 'medium'
            else:
                pillar.residual_label = 'high'

    @api.constrains('low_pct', 'medium_pct', 'high_pct')
    def _check_percentages(self):
        """Validate percentages sum to 100."""
        for pillar in self:
            total = (pillar.low_pct or 0) + (pillar.medium_pct or 0) + (pillar.high_pct or 0)
            if total > 0 and abs(total - 100.0) > 0.01:  # Allow small rounding errors
                raise ValidationError(_('Risk distribution percentages must sum to 100%.'))

    @api.constrains('control_pct', 'custom_control_pct', 'control_band')
    def _check_control_pct(self):
        """Validate control percentage range."""
        for pillar in self:
            if pillar.control_pct and (pillar.control_pct < 0 or pillar.control_pct > 100):
                raise ValidationError(_('Control effectiveness must be between 0% and 100%.'))
            if pillar.control_band == 'custom':
                if not pillar.custom_control_pct:
                    raise ValidationError(_('Custom control percentage is required when control band is "Custom".'))
                if pillar.custom_control_pct < 0 or pillar.custom_control_pct > 100:
                    raise ValidationError(_('Custom control effectiveness must be between 0% and 100%.'))
