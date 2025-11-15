# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class EwraRun(models.Model):
    """Enterprise-Wide Risk Assessment Run."""
    _name = 'nexaml.ewra.run'
    _description = 'EWRA Run'
    _order = 'period_end desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='EWRA Name',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        help='Unique EWRA run identifier'
    )
    status = fields.Selection(
        [('draft', 'Draft'),
         ('in_progress', 'In Progress'),
         ('completed', 'Completed'),
         ('archived', 'Archived')],
        string='Status',
        required=True,
        default='draft',
        tracking=True,
        help='EWRA run status'
    )
    period_start = fields.Date(
        string='Period Start',
        required=True,
        tracking=True,
        help='Assessment period start date'
    )
    period_end = fields.Date(
        string='Period End',
        required=True,
        tracking=True,
        help='Assessment period end date'
    )

    # Relations
    pillar_ids = fields.One2many(
        'nexaml.ewra.pillar',
        'run_id',
        string='Risk Pillars',
        help='Risk assessment pillars'
    )
    settings_snapshot_id = fields.Many2one(
        'nexaml.ewra.settings.snapshot',
        string='Settings Snapshot',
        help='Settings at time of assessment'
    )
    narrative_id = fields.Many2one(
        'nexaml.ewra.narrative',
        string='Narrative',
        help='Foreword and conclusion'
    )

    # Overall Risk Scores
    overall_inherent_score = fields.Float(
        string='Overall Inherent Risk',
        compute='_compute_overall_scores',
        store=True,
        help='Weighted average inherent risk (1.0-3.0)'
    )
    overall_residual_score = fields.Float(
        string='Overall Residual Risk',
        compute='_compute_overall_scores',
        store=True,
        help='Weighted average residual risk (1.0-3.0)'
    )
    overall_risk_level = fields.Selection(
        [('low', 'Low'),
         ('medium', 'Medium'),
         ('high', 'High')],
        string='Overall Risk Level',
        compute='_compute_overall_scores',
        store=True,
        help='Overall risk classification'
    )

    # Compliance Officer Signature
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        help='Compliance officer who approved'
    )
    approved_date = fields.Datetime(
        string='Approved Date',
        help='When the EWRA was approved'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        help='Company'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate EWRA run number."""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('nexaml.ewra.run') or _('New')
        return super(EwraRun, self).create(vals_list)

    @api.depends('pillar_ids.inherent_score', 'pillar_ids.residual_score')
    def _compute_overall_scores(self):
        """Compute overall risk scores from pillars."""
        for run in self:
            if not run.pillar_ids:
                run.overall_inherent_score = 0.0
                run.overall_residual_score = 0.0
                run.overall_risk_level = 'low'
                continue

            # Average inherent and residual scores
            inherent_scores = run.pillar_ids.mapped('inherent_score')
            residual_scores = run.pillar_ids.mapped('residual_score')

            run.overall_inherent_score = sum(inherent_scores) / len(inherent_scores) if inherent_scores else 0.0
            run.overall_residual_score = sum(residual_scores) / len(residual_scores) if residual_scores else 0.0

            # Classify risk level based on residual score
            residual = run.overall_residual_score
            if residual < 1.7:
                run.overall_risk_level = 'low'
            elif residual < 2.4:
                run.overall_risk_level = 'medium'
            else:
                run.overall_risk_level = 'high'

    @api.constrains('period_start', 'period_end')
    def _check_period_dates(self):
        """Validate period dates."""
        for run in self:
            if run.period_start and run.period_end and run.period_start > run.period_end:
                raise ValidationError(_('Period start date must be before end date.'))

    def action_start_assessment(self):
        """Start the EWRA assessment."""
        self.write({'status': 'in_progress'})
        self.message_post(
            body=_('EWRA assessment started by %s') % self.env.user.name,
            subject=_('Assessment Started')
        )

    def action_complete(self):
        """Complete the EWRA assessment."""
        # Validate all pillars are assessed
        if not self.pillar_ids:
            raise ValidationError(_('Cannot complete EWRA without risk pillars.'))

        self.write({
            'status': 'completed',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now()
        })
        self.message_post(
            body=_('EWRA assessment completed by %s') % self.env.user.name,
            subject=_('Assessment Completed')
        )

    def action_archive(self):
        """Archive the EWRA run."""
        self.write({'status': 'archived'})

    def action_generate_pdf(self):
        """Generate EWRA PDF report."""
        return self.env.ref('nexaml.action_report_ewra').report_action(self)
