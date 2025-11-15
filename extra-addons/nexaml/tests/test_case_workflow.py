# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'nexaml')
class TestCaseWorkflow(TransactionCase):
    """Test case management workflow."""

    def setUp(self):
        super().setUp()
        self.Case = self.env['aml.case']
        self.Alert = self.env['aml.alert']
        self.Partner = self.env['res.partner']
        self.Rule = self.env['aml.transaction.rule']

        # Create test partner
        self.partner = self.Partner.create({
            'name': 'Test Customer',
            'customer_risk': '2',
            'geography_risk': '2',
            'product_risk': '2',
            'channel_risk': '2',
        })

        # Create test rule
        self.rule = self.Rule.create({
            'name': 'Test Rule',
            'code': 'TEST_RULE',
            'rule_type': 'threshold',
            'amount_threshold': 50000,
            'alert_severity': 'high',
        })

    def test_case_creation_with_sequence(self):
        """Test that case gets auto-generated number."""
        case = self.Case.create({
            'partner_id': self.partner.id,
            'case_type': 'transaction',
            'description': 'Test case',
        })

        self.assertNotEqual(case.name, 'New')
        self.assertIn('CASE', case.name)

    def test_case_workflow_states(self):
        """Test case workflow state transitions."""
        case = self.Case.create({
            'partner_id': self.partner.id,
            'case_type': 'transaction',
        })

        # Initial state
        self.assertEqual(case.state, 'open')

        # Investigate
        case.action_investigate()
        self.assertEqual(case.state, 'investigating')

        # Review
        case.action_review()
        self.assertEqual(case.state, 'review')

        # Resolve
        case.action_resolve()
        self.assertEqual(case.state, 'resolved')

        # Close
        case.action_close()
        self.assertEqual(case.state, 'closed')
        self.assertIsNotNone(case.closed_date)

    def test_alert_escalation_to_case(self):
        """Test escalating alert to case."""
        alert = self.Alert.create({
            'partner_id': self.partner.id,
            'rule_id': self.rule.id,
            'severity': 'high',
            'alert_reason': 'High value transaction',
        })

        self.assertEqual(alert.status, 'new')

        # Escalate to case
        action = alert.action_escalate_to_case()

        # Alert should be escalated
        self.assertEqual(alert.status, 'escalated')
        self.assertIsNotNone(alert.case_id)

        # Case should be created
        case = alert.case_id
        self.assertEqual(case.partner_id.id, self.partner.id)
        self.assertIn(alert, case.alert_ids)
        self.assertEqual(case.priority, 'high')

    def test_alert_close(self):
        """Test closing alert without escalation."""
        alert = self.Alert.create({
            'partner_id': self.partner.id,
            'rule_id': self.rule.id,
            'severity': 'low',
            'alert_reason': 'Minor issue',
        })

        alert.action_close()

        self.assertEqual(alert.status, 'closed')
        self.assertEqual(alert.reviewed_by.id, self.env.user.id)
        self.assertIsNotNone(alert.reviewed_date)

    def test_alert_investigation(self):
        """Test marking alert as investigating."""
        alert = self.Alert.create({
            'partner_id': self.partner.id,
            'rule_id': self.rule.id,
            'severity': 'medium',
            'alert_reason': 'Unusual pattern',
        })

        alert.action_investigate()

        self.assertEqual(alert.status, 'investigating')
        self.assertEqual(alert.reviewed_by.id, self.env.user.id)

    def test_case_alert_count(self):
        """Test case alert count computation."""
        case = self.Case.create({
            'partner_id': self.partner.id,
            'case_type': 'transaction',
        })

        # Create alerts
        alert1 = self.Alert.create({
            'partner_id': self.partner.id,
            'rule_id': self.rule.id,
            'severity': 'high',
            'alert_reason': 'Alert 1',
        })
        alert2 = self.Alert.create({
            'partner_id': self.partner.id,
            'rule_id': self.rule.id,
            'severity': 'medium',
            'alert_reason': 'Alert 2',
        })

        case.alert_ids = [(6, 0, [alert1.id, alert2.id])]

        self.assertEqual(case.alert_count, 2)

    def test_case_assignment(self):
        """Test case assignment to user."""
        user = self.env.user

        case = self.Case.create({
            'partner_id': self.partner.id,
            'case_type': 'transaction',
            'assigned_to': user.id,
        })

        self.assertEqual(case.assigned_to.id, user.id)

    def test_case_resolution_options(self):
        """Test case resolution options."""
        case = self.Case.create({
            'partner_id': self.partner.id,
            'case_type': 'transaction',
        })

        # Test different resolution types
        resolutions = ['no_action', 'customer_contacted', 'sar_filed',
                      'relationship_terminated', 'false_positive', 'other']

        for resolution in resolutions:
            case.resolution = resolution
            self.assertEqual(case.resolution, resolution)

    def test_partner_alert_count(self):
        """Test partner alert count computation."""
        # Create alerts for partner
        alert1 = self.Alert.create({
            'partner_id': self.partner.id,
            'rule_id': self.rule.id,
            'severity': 'high',
            'alert_reason': 'Alert 1',
            'status': 'new',
        })
        alert2 = self.Alert.create({
            'partner_id': self.partner.id,
            'rule_id': self.rule.id,
            'severity': 'medium',
            'alert_reason': 'Alert 2',
            'status': 'investigating',
        })
        alert3 = self.Alert.create({
            'partner_id': self.partner.id,
            'rule_id': self.rule.id,
            'severity': 'low',
            'alert_reason': 'Alert 3',
            'status': 'closed',
        })

        self.partner._compute_alert_count()

        # Should count new and investigating (not closed)
        self.assertEqual(self.partner.alert_count, 2)

    def test_chatter_integration(self):
        """Test chatter messages on case actions."""
        case = self.Case.create({
            'partner_id': self.partner.id,
            'case_type': 'transaction',
        })

        initial_message_count = len(case.message_ids)

        case.action_investigate()

        # Should have new message
        self.assertGreater(len(case.message_ids), initial_message_count)
