# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Control(models.Model):
    """Risk controls and mitigations for residual risk calculation."""
    _name = 'aml.control'
    _description = 'Risk Control'
    _order = 'name'

    name = fields.Char(
        string='Control Name',
        required=True,
        help='Name of the risk control or mitigation measure'
    )
    mitigation_factor = fields.Float(
        string='Mitigation Factor',
        required=True,
        default=1.0,
        help='Factor to reduce inherent risk (0.0-1.0). Lower values = stronger mitigation'
    )
    description = fields.Text(
        string='Description',
        help='Description of the control and how it mitigates risk'
    )
    partner_ids = fields.Many2many(
        'res.partner',
        'partner_control_rel',
        'control_id',
        'partner_id',
        string='Applied To Customers',
        help='Customers with this control applied'
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Control name must be unique!'),
        ('mitigation_factor_check',
         'CHECK(mitigation_factor >= 0.0 AND mitigation_factor <= 1.0)',
         'Mitigation factor must be between 0.0 and 1.0')
    ]
