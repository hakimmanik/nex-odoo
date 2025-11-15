# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class CraSettings(models.Model):
    """CRA Scenarios Settings Configuration."""
    _name = 'nexaml.cra.settings'
    _description = 'CRA Settings'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        help='Company these settings apply to'
    )

    # Critical Risk Factors (Overrides)
    pep_status_enabled = fields.Boolean(
        string='PEP Status',
        default=True,
        help='Enable PEP status override'
    )
    pep_status_action = fields.Selection(
        [('elevate_high', 'Elevate to High Risk'),
         ('block', 'Block Customer')],
        string='PEP Action',
        default='elevate_high',
        help='Action to take when PEP is detected'
    )

    high_risk_jurisdiction_enabled = fields.Boolean(
        string='High Risk Jurisdiction',
        default=True,
        help='Enable high risk jurisdiction override'
    )
    high_risk_jurisdiction_action = fields.Selection(
        [('elevate_high', 'Elevate to High Risk'),
         ('block', 'Block Customer')],
        string='High Risk Jurisdiction Action',
        default='elevate_high',
        help='Action for high risk jurisdiction'
    )

    opaque_ownership_enabled = fields.Boolean(
        string='Opaque Ownership',
        default=True,
        help='Enable opaque ownership structure override'
    )
    opaque_ownership_action = fields.Selection(
        [('elevate_high', 'Elevate to High Risk'),
         ('block', 'Block Customer')],
        string='Opaque Ownership Action',
        default='elevate_high',
        help='Action for opaque ownership structures'
    )

    confirmed_sanctions_enabled = fields.Boolean(
        string='Confirmed Sanctions',
        default=True,
        help='Enable confirmed sanctions match override'
    )
    confirmed_sanctions_action = fields.Selection(
        [('elevate_high', 'Elevate to High Risk'),
         ('block', 'Block Customer')],
        string='Sanctions Action',
        default='block',
        help='Action for confirmed sanctions match'
    )

    # Regulatory Scenarios
    sar_str_filed_enabled = fields.Boolean(
        string='SAR/STR Filed',
        default=True,
        help='Enable SAR/STR filing scenario'
    )
    sar_str_filed_action = fields.Selection(
        [('elevate_high', 'Elevate to High Risk'),
         ('block', 'Block Customer')],
        string='SAR/STR Action',
        default='elevate_high',
        help='Action when SAR/STR is filed'
    )

    law_enforcement_enquiry_enabled = fields.Boolean(
        string='Law Enforcement Enquiry',
        default=True,
        help='Enable law enforcement enquiry scenario'
    )
    law_enforcement_enquiry_action = fields.Selection(
        [('elevate_high', 'Elevate to High Risk'),
         ('block', 'Block Customer')],
        string='Law Enforcement Action',
        default='elevate_high',
        help='Action for law enforcement enquiry'
    )

    # Reputational Scenarios
    adverse_media_confirmed_enabled = fields.Boolean(
        string='Adverse Media Confirmed',
        default=True,
        help='Enable adverse media scenario'
    )
    adverse_media_confirmed_action = fields.Selection(
        [('elevate_high', 'Elevate to High Risk'),
         ('block', 'Block Customer')],
        string='Adverse Media Action',
        default='elevate_high',
        help='Action for confirmed adverse media'
    )

    _sql_constraints = [
        ('company_unique', 'UNIQUE(company_id)',
         'Only one CRA settings record allowed per company!')
    ]

    @api.model
    def get_settings(self, company_id=None):
        """Get CRA settings for company, create defaults if not exists."""
        if not company_id:
            company_id = self.env.company.id

        settings = self.search([('company_id', '=', company_id)], limit=1)
        if not settings:
            settings = self.create({'company_id': company_id})

        return settings

    def action_open_cra_settings(self):
        """Open CRA settings form, creating record if needed."""
        settings = self.get_settings()
        return {
            'type': 'ir.actions.act_window',
            'name': _('CRA Settings'),
            'res_model': 'nexaml.cra.settings',
            'res_id': settings.id,
            'view_mode': 'form',
            'target': 'current',
        }
