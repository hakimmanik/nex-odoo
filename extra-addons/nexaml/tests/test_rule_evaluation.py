# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'nexaml')
class TestRuleEvaluation(TransactionCase):
    """Test transaction monitoring rule evaluation."""

    def setUp(self):
        super().setUp()
        self.Rule = self.env['aml.transaction.rule']
        self.Partner = self.env['res.partner']
        self.AccountMove = self.env['account.move']

        # Create test partner
        self.partner = self.Partner.create({
            'name': 'Test Customer',
            'customer_risk': '2',
            'geography_risk': '2',
            'product_risk': '2',
            'channel_risk': '2',
        })

        # Create test currency
        self.currency = self.env.ref('base.USD')

    def test_threshold_rule_triggers(self):
        """Test that threshold rule triggers for high amounts."""
        rule = self.Rule.create({
            'name': 'High Value Test',
            'code': 'HIGH_VALUE_TEST',
            'rule_type': 'threshold',
            'amount_threshold': 50000,
            'currency_id': self.currency.id,
            'alert_severity': 'high',
        })

        move = self.AccountMove.create({
            'partner_id': self.partner.id,
            'move_type': 'out_invoice',
            'date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': 'Test Service',
                'price_unit': 60000,
                'quantity': 1,
            })],
        })

        result = rule.evaluate(move)
        self.assertTrue(result['triggered'])
        self.assertIn('60000', result['reason'])

    def test_threshold_rule_not_triggers(self):
        """Test that threshold rule doesn't trigger for low amounts."""
        rule = self.Rule.create({
            'name': 'High Value Test',
            'code': 'HIGH_VALUE_TEST',
            'rule_type': 'threshold',
            'amount_threshold': 50000,
            'currency_id': self.currency.id,
            'alert_severity': 'high',
        })

        move = self.AccountMove.create({
            'partner_id': self.partner.id,
            'move_type': 'out_invoice',
            'date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': 'Test Service',
                'price_unit': 30000,
                'quantity': 1,
            })],
        })

        result = rule.evaluate(move)
        self.assertFalse(result['triggered'])

    def test_velocity_rule_transaction_count(self):
        """Test velocity rule based on transaction count."""
        rule = self.Rule.create({
            'name': 'Velocity Test',
            'code': 'VELOCITY_TEST',
            'rule_type': 'velocity',
            'period_days': 1,
            'transaction_count': 3,
            'alert_severity': 'medium',
        })

        # Create 4 transactions on same day
        for i in range(4):
            move = self.AccountMove.create({
                'partner_id': self.partner.id,
                'move_type': 'out_invoice',
                'date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, {
                    'name': f'Test Service {i}',
                    'price_unit': 1000,
                    'quantity': 1,
                })],
            })
            move.action_post()

        # Evaluate last move
        result = rule.evaluate(move)
        self.assertTrue(result['triggered'])
        self.assertIn('4 transactions', result['reason'])

    def test_velocity_rule_amount(self):
        """Test velocity rule based on total amount."""
        rule = self.Rule.create({
            'name': 'Velocity Amount Test',
            'code': 'VELOCITY_AMOUNT_TEST',
            'rule_type': 'velocity',
            'period_days': 1,
            'velocity_amount': 100000,
            'currency_id': self.currency.id,
            'alert_severity': 'high',
        })

        # Create 3 transactions totaling over 100k
        for i in range(3):
            move = self.AccountMove.create({
                'partner_id': self.partner.id,
                'move_type': 'out_invoice',
                'date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, {
                    'name': f'Test Service {i}',
                    'price_unit': 40000,
                    'quantity': 1,
                })],
            })
            move.action_post()

        result = rule.evaluate(move)
        self.assertTrue(result['triggered'])
        self.assertIn('120000', result['reason'])

    def test_risk_level_filtering(self):
        """Test that rules can be filtered by partner risk level."""
        # Rule only applies to high risk
        rule = self.Rule.create({
            'name': 'High Risk Only',
            'code': 'HIGH_RISK_ONLY',
            'rule_type': 'threshold',
            'amount_threshold': 10000,
            'currency_id': self.currency.id,
            'applies_to_risk_level': 'high',
            'alert_severity': 'high',
        })

        # Low risk partner
        low_partner = self.Partner.create({
            'name': 'Low Risk Customer',
            'customer_risk': '1',
            'geography_risk': '1',
            'product_risk': '1',
            'channel_risk': '1',
        })

        move = self.AccountMove.create({
            'partner_id': low_partner.id,
            'move_type': 'out_invoice',
            'date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': 'Test Service',
                'price_unit': 15000,
                'quantity': 1,
            })],
        })

        result = rule.evaluate(move)
        self.assertFalse(result['triggered'])
        self.assertIn('Risk level not applicable', result['reason'])

    def test_pattern_rule_with_domain(self):
        """Test pattern matching rule with domain filter."""
        rule = self.Rule.create({
            'name': 'Round Amount Pattern',
            'code': 'ROUND_AMOUNT',
            'rule_type': 'pattern',
            'domain_filter': "[('amount_total', '>=', 10000), ('name', 'ilike', 'INV')]",
            'alert_severity': 'low',
        })

        move = self.AccountMove.create({
            'partner_id': self.partner.id,
            'move_type': 'out_invoice',
            'date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': 'Test Service',
                'price_unit': 15000,
                'quantity': 1,
            })],
        })
        move.action_post()

        result = rule.evaluate(move)
        self.assertTrue(result['triggered'])

    def test_transaction_risk_score_calculation(self):
        """Test transaction risk score calculation."""
        # Create high-value transaction for high-risk partner
        high_partner = self.Partner.create({
            'name': 'High Risk Customer',
            'customer_risk': '3',
            'geography_risk': '3',
            'product_risk': '3',
            'channel_risk': '3',
        })

        move = self.AccountMove.create({
            'partner_id': high_partner.id,
            'move_type': 'out_invoice',
            'date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': 'High Value Service',
                'price_unit': 150000,
                'quantity': 1,
            })],
        })

        # Risk score should be high (amount: 40 + partner risk: 30 = 70+)
        self.assertGreater(move.risk_score, 60)
