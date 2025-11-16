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
    risk_preview_json = fields.Text(
        string='Risk Preview Data',
        compute='_compute_risk_preview',
        help='JSON data for risk preview'
    )
    risk_preview_html = fields.Html(
        string='Risk Preview',
        compute='_compute_risk_preview',
        help='Risk factors preview before posting'
    )
    partner_risk_level = fields.Selection(
        related='partner_id.risk_level',
        string='Partner Risk Level',
        readonly=True
    )
    partner_inherent_risk = fields.Float(
        related='partner_id.inherent_risk',
        string='Partner Inherent Risk',
        readonly=True
    )
    partner_residual_risk = fields.Float(
        related='partner_id.residual_risk',
        string='Partner Residual Risk',
        readonly=True
    )

    @api.depends('alert_ids')
    def _compute_alert_count(self):
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

    @api.depends('partner_id', 'amount_total', 'invoice_payment_term_id', 'preferred_payment_method_line_id', 'move_type', 'state')
    def _compute_risk_preview(self):
        for move in self:
            if not move.partner_id or move.state == 'posted':
                move.risk_preview_json = '{}'
                move.risk_preview_html = ''
                continue

            partner = move.partner_id
            amount = abs(move.amount_total or 0)

            open_cases = self.env['aml.case'].search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['open', 'investigating', 'under_review', 'pending_info'])
            ], limit=5)

            has_sanctions = bool(self.env['aml.case'].search_count([
                ('partner_id', '=', partner.id),
                ('case_type', '=', 'sanction'),
                ('state', '!=', 'resolved_approved')
            ], limit=1))

            is_pep = partner.pep_status or bool(self.env['aml.case'].search_count([
                ('partner_id', '=', partner.id),
                ('case_type', '=', 'pep'),
                ('state', '!=', 'resolved_approved')
            ], limit=1))

            risk_factors = []

            is_crypto = False
            is_third_party = False
            is_high_risk_payment = False

            if move.preferred_payment_method_line_id and move.preferred_payment_method_line_id.payment_method_id:
                payment_method = move.preferred_payment_method_line_id.payment_method_id
                method_name = (payment_method.name or '').lower()

                if 'crypto' in method_name or 'bitcoin' in method_name or 'btc' in method_name or 'ethereum' in method_name:
                    is_crypto = True

                if payment_method.risk_score == '3':
                    is_high_risk_payment = True

            if move.invoice_payment_term_id:
                term_name = (move.invoice_payment_term_id.name or '').lower()
                if 'third' in term_name or 'party' in term_name or 'escrow' in term_name:
                    is_third_party = True

            if is_crypto:
                risk_factors.append(('crypto', 'Cryptocurrency transaction'))
            if is_third_party:
                risk_factors.append(('third_party', 'Third-party payment'))
            if amount > 10000:
                risk_factors.append(('large_amount', 'Large transaction amount'))
            if is_high_risk_payment:
                risk_factors.append(('high_risk_payment', 'High-risk payment type'))
            if partner.country_id and partner.country_id.code in ['AF', 'IR', 'KP', 'SY', 'YE']:
                risk_factors.append(('high_risk_country', 'High-risk jurisdiction'))

            rules = self.env['aml.transaction.rule'].search([('active', '=', True)])
            triggered_rules = []
            for rule in rules:
                try:
                    result = rule.evaluate(move)
                    if result.get('triggered'):
                        triggered_rules.append({
                            'name': rule.name,
                            'severity': rule.alert_severity,
                            'reason': result.get('reason', ''),
                        })
                except Exception:
                    pass

            html_parts = []
            html_parts.append('<div style="padding: 15px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; margin: 10px 0;">')

            html_parts.append('<div style="margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #ffc107;">')
            html_parts.append(f'<strong style="font-size: 14px;">Partner:</strong> <span style="font-size: 14px;">{partner.name}</span>')
            html_parts.append('</div>')

            if open_cases:
                html_parts.append('<div style="margin-bottom: 15px;">')
                html_parts.append('<strong style="color: #856404;">⚠ Open Cases:</strong>')
                html_parts.append(f'<span style="margin-left: 10px; background: #fff3cd; padding: 2px 8px; border-radius: 3px;">{len(open_cases)} Active</span>')
                html_parts.append('</div>')

            flags = []
            if has_sanctions:
                flags.append('<span style="background: #f8d7da; color: #721c24; padding: 3px 8px; border-radius: 3px; margin-right: 5px;">Sanctioned</span>')
            if is_pep:
                flags.append('<span style="background: #fff3cd; color: #856404; padding: 3px 8px; border-radius: 3px; margin-right: 5px;">PEP</span>')

            if flags:
                html_parts.append('<div style="margin-bottom: 15px;">')
                html_parts.append('<strong>Compliance Flags:</strong><br/>')
                html_parts.append(''.join(flags))
                html_parts.append('</div>')

            html_parts.append('<div style="margin-bottom: 15px; background: white; padding: 10px; border-radius: 4px;">')
            html_parts.append('<strong style="font-size: 13px; display: block; margin-bottom: 8px;">Risk Scores:</strong>')

            risk_level_color = {'low': '#28a745', 'medium': '#ffc107', 'high': '#dc3545', 'blocked': '#6c757d'}
            color = risk_level_color.get(partner.risk_level or 'low', '#6c757d')

            inherent_score = partner.inherent_risk or 0
            residual_score = partner.residual_risk or 0

            html_parts.append(f'<div style="margin-bottom: 6px; padding: 4px 8px; background: #f8f9fa; border-radius: 3px;"><strong>Risk Level:</strong> <span style="color: {color}; font-weight: bold;">{(partner.risk_level or "low").upper()}</span></div>')
            html_parts.append(f'<div style="margin-bottom: 6px; padding: 4px 8px; background: #f8f9fa; border-radius: 3px;"><strong>Inherent Risk:</strong> {inherent_score:.0f}/100</div>')
            html_parts.append(f'<div style="margin-bottom: 6px; padding: 4px 8px; background: #f8f9fa; border-radius: 3px;"><strong>Residual Risk:</strong> {residual_score:.0f}/100</div>')
            html_parts.append('</div>')

            if risk_factors or triggered_rules:
                html_parts.append('<div style="background: white; padding: 10px; border-radius: 4px;">')
                html_parts.append('<strong style="font-size: 13px; display: block; margin-bottom: 8px;">Risk Factors:</strong>')
                html_parts.append('<ul style="margin: 0; padding-left: 20px;">')
                for code, label in risk_factors:
                    html_parts.append(f'<li style="color: #856404; margin-bottom: 4px;">{label}</li>')
                for rule in triggered_rules:
                    severity_color = {'low': '#17a2b8', 'medium': '#ffc107', 'high': '#fd7e14', 'critical': '#dc3545'}
                    color = severity_color.get(rule['severity'], '#6c757d')
                    html_parts.append(f'<li style="color: {color}; margin-bottom: 4px;"><strong>{rule["name"]}</strong>: {rule["reason"]}</li>')
                html_parts.append('</ul></div>')
            else:
                html_parts.append('<div style="background: #d4edda; padding: 10px; border-radius: 4px; color: #155724;">')
                html_parts.append('✓ No additional risk factors identified')
                html_parts.append('</div>')

            html_parts.append('</div>')

            move.risk_preview_html = ''.join(html_parts)
            move.risk_preview_json = '{}'

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
