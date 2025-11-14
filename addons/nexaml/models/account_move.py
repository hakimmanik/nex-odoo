# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    """Extend account.move for AML transaction monitoring."""
    _inherit = 'account.move'

    # Monitoring Fields
    monitored = fields.Boolean(
        string='Monitored',
        default=False,
        help='Whether this transaction has been screened by rules'
    )
    risk_score = fields.Float(
        string='Risk Score',
        compute='_compute_risk_score',
        store=True,
        help='Transaction risk score based on amount, partner risk, and alerts'
    )
    alert_ids = fields.One2many(
        'aml.alert',
        'move_id',
        string='Alerts',
        help='Alerts generated for this transaction'
    )
    alert_count = fields.Integer(
        string='Alert Count',
        compute='_compute_alert_count',
        help='Number of alerts'
    )

    @api.depends('alert_ids')
    def _compute_alert_count(self):
        """Count alerts."""
        for move in self:
            move.alert_count = len(move.alert_ids)

    @api.depends('amount_total', 'partner_id.risk_level', 'alert_count')
    def _compute_risk_score(self):
        """Calculate transaction risk score."""
        for move in self:
            score = 0.0

            # Amount factor (0-40 points)
            amount = abs(move.amount_total)
            if amount > 100000:
                score += 40
            elif amount > 50000:
                score += 30
            elif amount > 10000:
                score += 20
            elif amount > 5000:
                score += 10

            # Partner risk factor (0-30 points)
            if move.partner_id:
                partner_risk = move.partner_id.risk_level
                if partner_risk == 'high':
                    score += 30
                elif partner_risk == 'medium':
                    score += 15

            # Alert count factor (0-30 points)
            if move.alert_count > 3:
                score += 30
            elif move.alert_count > 1:
                score += 20
            elif move.alert_count > 0:
                score += 10

            move.risk_score = score

    def _check_rules(self):
        """Check transaction against all active rules."""
        self.ensure_one()

        # Get configuration
        ICP = self.env['ir.config_parameter'].sudo()
        monitor_invoices = ICP.get_param('nexaml.monitor_invoices', 'True') == 'True'
        monitor_payments = ICP.get_param('nexaml.monitor_payments', 'True') == 'True'

        # Check if monitoring is enabled for this move type
        if self.move_type in ['out_invoice', 'in_invoice'] and not monitor_invoices:
            return
        if self.move_type in ['out_receipt', 'in_receipt'] and not monitor_payments:
            return

        # Skip if already monitored
        if self.monitored:
            return

        # Get active rules
        rules = self.env['aml.transaction.rule'].search([('active', '=', True)])

        alerts_created = 0

        for rule in rules:
            try:
                result = rule.evaluate(self)

                if result.get('triggered'):
                    # Create alert
                    alert_vals = {
                        'partner_id': self.partner_id.id,
                        'move_id': self.id,
                        'rule_id': rule.id,
                        'severity': rule.alert_severity,
                        'alert_reason': result.get('reason', 'Rule triggered'),
                        'alert_details': str(result.get('details', {})),
                        'triggered_value': result.get('details', {}).get('amount', 0),
                    }

                    alert = self.env['aml.alert'].create(alert_vals)
                    alerts_created += 1

                    _logger.info('Alert created: %s for transaction %s (rule: %s)',
                                alert.name, self.name, rule.code)

            except Exception as e:
                _logger.error('Error evaluating rule %s for move %s: %s',
                             rule.code, self.name, str(e))

        # Mark as monitored
        self.monitored = True

        if alerts_created > 0:
            _logger.info('Created %d alerts for transaction %s',
                        alerts_created, self.name)

        return alerts_created

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to check AML rules."""
        moves = super(AccountMove, self).create(vals_list)

        # Check rules for posted moves
        for move in moves:
            if move.state == 'posted' and move.move_type in ['out_invoice', 'in_invoice', 'out_receipt', 'in_receipt']:
                try:
                    move._check_rules()
                except Exception as e:
                    _logger.error('Rule checking failed for move %s: %s',
                                 move.name, str(e))

        return moves

    def action_post(self):
        """Override post to check rules."""
        result = super(AccountMove, self).action_post()

        # Check rules after posting
        for move in self:
            if move.move_type in ['out_invoice', 'in_invoice', 'out_receipt', 'in_receipt']:
                try:
                    move._check_rules()
                except Exception as e:
                    _logger.error('Rule checking failed for move %s: %s',
                                 move.name, str(e))

        return result
