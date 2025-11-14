# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

from unittest.mock import patch, MagicMock
from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'nexaml', 'integration')
class TestIntegration(TransactionCase):
    """End-to-end integration tests for NexAML workflows."""

    def setUp(self):
        super().setUp()
        self.Partner = self.env['res.partner']
        self.AccountMove = self.env['account.move']
        self.Case = self.env['aml.case']
        self.Alert = self.env['aml.alert']
        self.Rule = self.env['aml.transaction.rule']
        self.Screening = self.env['aml.screening']

        # Configure system
        self.env['ir.config_parameter'].sudo().set_param('nexaml.yente_url', 'https://sanctions.nex.systems/match/default')
        self.env['ir.config_parameter'].sudo().set_param('nexaml.screening_threshold', '70.0')
        self.env['ir.config_parameter'].sudo().set_param('nexaml.monitor_invoices', 'True')
        self.env['ir.config_parameter'].sudo().set_param('nexaml.auto_screen_on_create', 'False')

        # Create currency
        self.currency = self.env.ref('base.USD')

    @patch('requests.post')
    def test_full_transaction_workflow(self, mock_post):
        """Test complete workflow: partner → transaction → alert → case → resolution."""

        # Mock screening API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': []}
        mock_post.return_value = mock_response

        # 1. Create partner with risk assessment
        partner = self.Partner.create({
            'name': 'High Risk Customer',
            'customer_risk': '3',
            'geography_risk': '3',
            'product_risk': '3',
            'channel_risk': '3',
        })

        # Verify risk calculation
        self.assertEqual(partner.risk_level, 'high')
        self.assertEqual(partner.inherent_risk, 3.0)

        # 2. Screen partner
        partner.action_screen_sanctions()
        screenings = self.Screening.search([('partner_id', '=', partner.id)])
        self.assertGreater(len(screenings), 0)

        # 3. Create transaction rule
        rule = self.Rule.create({
            'name': 'High Value Rule',
            'code': 'HIGH_VALUE_INTEGRATION',
            'rule_type': 'threshold',
            'amount_threshold': 50000,
            'currency_id': self.currency.id,
            'alert_severity': 'high',
            'active': True,
        })

        # 4. Create high-value transaction
        move = self.AccountMove.create({
            'partner_id': partner.id,
            'move_type': 'out_invoice',
            'date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': 'High Value Service',
                'price_unit': 75000,
                'quantity': 1,
            })],
        })
        move.action_post()

        # 5. Verify alert was created
        alerts = self.Alert.search([('move_id', '=', move.id)])
        self.assertGreater(len(alerts), 0)
        alert = alerts[0]
        self.assertEqual(alert.severity, 'high')
        self.assertEqual(alert.partner_id.id, partner.id)

        # 6. Escalate alert to case
        alert.action_escalate_to_case()
        self.assertEqual(alert.status, 'escalated')
        case = alert.case_id
        self.assertIsNotNone(case)

        # 7. Work through case workflow
        case.action_investigate()
        self.assertEqual(case.state, 'investigating')

        case.write({
            'investigation_notes': '<p>Investigation completed. Transaction appears legitimate.</p>',
            'resolution': 'no_action',
        })

        case.action_resolve()
        self.assertEqual(case.state, 'resolved')

        case.action_close()
        self.assertEqual(case.state, 'closed')
        self.assertIsNotNone(case.closed_date)

    @patch('requests.post')
    def test_sanctions_match_workflow(self, mock_post):
        """Test workflow when sanctions match is found."""

        # Mock API response with match
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [{
                'id': 'entity-456',
                'caption': 'Sanctioned Entity',
                'score': 0.95,
                'properties': {
                    'name': ['Sanctioned Entity'],
                    'country': ['XX'],
                },
                'datasets': ['sanctions-list'],
            }]
        }
        mock_post.return_value = mock_response

        # 1. Create partner
        partner = self.Partner.create({
            'name': 'Sanctioned Entity',
            'is_company': True,
        })

        # 2. Screen and detect match
        partner.action_screen_sanctions()

        # 3. Verify match was recorded
        screenings = self.Screening.search([
            ('partner_id', '=', partner.id),
            ('status', '=', 'match')
        ])
        self.assertGreater(len(screenings), 0)
        screening = screenings[0]
        self.assertEqual(screening.match_score, 95.0)

        # 4. Partner sanctions status should be updated
        partner._compute_sanctions_status()
        self.assertEqual(partner.sanctions_status, 'match')

        # 5. Mark as false positive if needed
        screening.write({'review_notes': 'Different entity with same name'})
        screening.action_mark_false_positive()
        self.assertEqual(screening.status, 'false_positive')

    def test_velocity_monitoring_workflow(self):
        """Test velocity monitoring across multiple transactions."""

        # 1. Create velocity rule
        rule = self.Rule.create({
            'name': 'Rapid Transactions',
            'code': 'RAPID_TRANS_INT',
            'rule_type': 'velocity',
            'period_days': 1,
            'transaction_count': 5,
            'alert_severity': 'high',
            'active': True,
        })

        # 2. Create partner
        partner = self.Partner.create({
            'name': 'Velocity Test Customer',
            'customer_risk': '2',
            'geography_risk': '2',
            'product_risk': '2',
            'channel_risk': '2',
        })

        # 3. Create multiple transactions rapidly
        moves = []
        for i in range(6):
            move = self.AccountMove.create({
                'partner_id': partner.id,
                'move_type': 'out_invoice',
                'date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, {
                    'name': f'Service {i}',
                    'price_unit': 10000,
                    'quantity': 1,
                })],
            })
            move.action_post()
            moves.append(move)

        # 4. Check that alert was generated for last transaction
        alerts = self.Alert.search([('partner_id', '=', partner.id)])
        self.assertGreater(len(alerts), 0)

        # 5. Verify alert details
        alert = alerts[0]
        self.assertEqual(alert.severity, 'high')
        self.assertIn('transactions', alert.alert_reason.lower())

    def test_report_generation_workflow(self):
        """Test report generation from case."""

        # 1. Create partner and case
        partner = self.Partner.create({
            'name': 'Report Test Customer',
            'customer_risk': '3',
            'geography_risk': '3',
            'product_risk': '3',
            'channel_risk': '3',
        })

        case = self.Case.create({
            'partner_id': partner.id,
            'case_type': 'transaction',
            'description': 'Suspicious activity detected',
            'investigation_notes': '<p>Detailed investigation findings...</p>',
            'resolution': 'sar_filed',
        })

        # 2. Create report wizard
        wizard = self.env['report.wizard'].create({
            'report_type': 'sar',
            'date_from': fields.Date.today(),
            'date_to': fields.Date.today(),
            'case_ids': [(6, 0, [case.id])],
            'output_format': 'pdf',
            'include_narrative': True,
        })

        # 3. Generate report
        action = wizard.action_generate_report()

        # 4. Verify report action returned
        self.assertIn('type', action)
        self.assertEqual(action['type'], 'ir.actions.report')

    def test_multi_alert_case_escalation(self):
        """Test case with multiple related alerts."""

        # 1. Create partner
        partner = self.Partner.create({
            'name': 'Multi-Alert Customer',
            'customer_risk': '2',
            'geography_risk': '2',
            'product_risk': '2',
            'channel_risk': '2',
        })

        # 2. Create multiple rules
        rule1 = self.Rule.create({
            'name': 'Rule 1',
            'code': 'RULE1_INT',
            'rule_type': 'threshold',
            'amount_threshold': 30000,
            'currency_id': self.currency.id,
            'alert_severity': 'medium',
            'active': True,
        })

        rule2 = self.Rule.create({
            'name': 'Rule 2',
            'code': 'RULE2_INT',
            'rule_type': 'threshold',
            'amount_threshold': 40000,
            'currency_id': self.currency.id,
            'alert_severity': 'high',
            'active': True,
        })

        # 3. Create transaction that triggers both rules
        move = self.AccountMove.create({
            'partner_id': partner.id,
            'move_type': 'out_invoice',
            'date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': 'Service',
                'price_unit': 45000,
                'quantity': 1,
            })],
        })
        move.action_post()

        # 4. Check that multiple alerts were created
        alerts = self.Alert.search([('partner_id', '=', partner.id)])
        self.assertGreaterEqual(len(alerts), 2)

        # 5. Create case and link all alerts
        case = self.Case.create({
            'partner_id': partner.id,
            'case_type': 'transaction',
            'alert_ids': [(6, 0, alerts.ids)],
            'move_ids': [(6, 0, [move.id])],
        })

        # 6. Verify case has all alerts and transaction
        self.assertEqual(len(case.alert_ids), len(alerts))
        self.assertEqual(case.move_count, 1)

    def test_risk_assessment_update_flow(self):
        """Test updating risk assessment after initial creation."""

        # 1. Create partner with low risk
        partner = self.Partner.create({
            'name': 'Risk Update Customer',
            'customer_risk': '1',
            'geography_risk': '1',
            'product_risk': '1',
            'channel_risk': '1',
        })

        # Initial risk
        self.assertEqual(partner.risk_level, 'low')
        initial_inherent = partner.inherent_risk

        # 2. Update risk factors
        partner.write({
            'customer_risk': '3',
            'geography_risk': '3',
            'product_risk': '3',
            'channel_risk': '3',
        })

        # 3. Verify risk recalculated
        self.assertEqual(partner.risk_level, 'high')
        self.assertGreater(partner.inherent_risk, initial_inherent)

        # 4. Add control to reduce residual risk
        control = self.env['aml.control'].create({
            'name': 'Enhanced Monitoring',
            'mitigation_factor': 0.6,
        })
        partner.control_ids = [(6, 0, [control.id])]

        # 5. Verify residual risk reduced
        self.assertLess(partner.residual_risk, partner.inherent_risk)
