# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    """Extend product.template with risk assessment fields."""
    _inherit = 'product.template'

    risk_score = fields.Selection(
        [('1', 'Low Risk'), ('2', 'Medium Risk'), ('3', 'High Risk')],
        string='Risk Score',
        default='1',
        help='Risk classification: 1=Low, 2=Medium, 3=High'
    )
