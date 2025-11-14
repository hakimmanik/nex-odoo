# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountPaymentMethod(models.Model):
    """Extend payment methods with risk scoring."""
    _inherit = 'account.payment.method'

    risk_score = fields.Selection(
        [('1', 'Low Risk'),
         ('2', 'Medium Risk'),
         ('3', 'High Risk')],
        string='Risk Score',
        default='2',
        help='Risk classification for this payment method:\n'
             '• Low (1): In-person, bank transfers with full documentation\n'
             '• Medium (2): Standard electronic payments\n'
             '• High (3): Cash, cryptocurrency, international wire, prepaid cards'
    )
