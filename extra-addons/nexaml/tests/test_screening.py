# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

from unittest.mock import patch, MagicMock
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'nexaml')
class TestScreening(TransactionCase):
    """Test sanctions screening functionality."""

    def setUp(self):
        super().setUp()
        self.Partner = self.env['res.partner']
        self.Screening = self.env['aml.screening']

        # Set up test configuration
        self.env['ir.config_parameter'].sudo().set_param('nexaml.yente_url', 'https://sanctions.nex.systems/match/default')
        self.env['ir.config_parameter'].sudo().set_param('nexaml.screening_threshold', '70.0')

    @patch('requests.post')
    def test_screening_api_call(self, mock_post):
        """Test that screening makes correct API call."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [{
                'id': 'entity-123',
                'caption': 'John Doe',
                'schema': 'Person',
                'score': 0.85,
                'properties': {
                    'name': ['John Doe'],
                    'country': ['US'],
                },
                'datasets': ['sanctions-list'],
            }]
        }
        mock_post.return_value = mock_response

        partner = self.Partner.create({
            'name': 'John Doe',
            'is_company': False,
        })

        partner.action_screen_sanctions()

        # Verify API was called
        self.assertTrue(mock_post.called)
        call_args = mock_post.call_args
        self.assertIn('yente', call_args[0][0])

    @patch('requests.post')
    def test_screening_match_created(self, mock_post):
        """Test that screening match creates record."""
        # Mock API response with match
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [{
                'id': 'entity-123',
                'caption': 'John Doe',
                'score': 0.85,
                'properties': {
                    'name': ['John Doe'],
                    'country': ['US'],
                },
                'datasets': ['sanctions-list'],
            }]
        }
        mock_post.return_value = mock_response

        partner = self.Partner.create({
            'name': 'John Doe',
            'is_company': False,
        })

        partner.action_screen_sanctions()

        # Check screening record created
        screenings = self.Screening.search([('partner_id', '=', partner.id)])
        self.assertEqual(len(screenings), 1)
        self.assertEqual(screenings[0].status, 'match')
        self.assertEqual(screenings[0].match_score, 85.0)

    @patch('requests.post')
    def test_screening_no_match(self, mock_post):
        """Test screening when no match found."""
        # Mock API response with no results
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': []}
        mock_post.return_value = mock_response

        partner = self.Partner.create({
            'name': 'Clean Customer',
            'is_company': False,
        })

        partner.action_screen_sanctions()

        screenings = self.Screening.search([('partner_id', '=', partner.id)])
        self.assertEqual(len(screenings), 1)
        self.assertEqual(screenings[0].status, 'clear')

    @patch('requests.post')
    def test_screening_below_threshold(self, mock_post):
        """Test that matches below threshold are not flagged."""
        # Mock API response with low score
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [{
                'id': 'entity-123',
                'caption': 'John Smith',
                'score': 0.50,  # Below 70% threshold
                'properties': {'name': ['John Smith']},
                'datasets': ['sanctions-list'],
            }]
        }
        mock_post.return_value = mock_response

        partner = self.Partner.create({
            'name': 'John Smith',
            'is_company': False,
        })

        partner.action_screen_sanctions()

        screenings = self.Screening.search([('partner_id', '=', partner.id)])
        # Should create clear record, not match
        self.assertEqual(screenings[0].status, 'clear')

    def test_false_positive_marking(self):
        """Test marking screening as false positive."""
        partner = self.Partner.create({'name': 'Test Partner'})

        screening = self.Screening.create({
            'partner_id': partner.id,
            'screening_type': 'sanctions',
            'status': 'match',
            'match_score': 85,
            'matched_name': 'Test Name',
        })

        screening.action_mark_false_positive()

        self.assertEqual(screening.status, 'false_positive')
        self.assertEqual(screening.reviewed_by.id, self.env.user.id)
        self.assertIsNotNone(screening.review_date)

    @patch('requests.post')
    def test_auto_screening_on_create(self, mock_post):
        """Test automatic screening when partner is created."""
        # Enable auto-screening
        self.env['ir.config_parameter'].sudo().set_param('nexaml.auto_screen_on_create', 'True')

        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': []}
        mock_post.return_value = mock_response

        partner = self.Partner.create({
            'name': 'New Customer',
            'is_company': False,
        })

        # Should have screening record from auto-screen
        screenings = self.Screening.search([('partner_id', '=', partner.id)])
        self.assertGreater(len(screenings), 0)

    def test_sanctions_status_update(self):
        """Test that partner sanctions status updates correctly."""
        partner = self.Partner.create({'name': 'Test Partner'})

        # No screening - should be not_screened
        self.assertEqual(partner.sanctions_status, 'not_screened')

        # Create clear screening
        self.Screening.create({
            'partner_id': partner.id,
            'screening_type': 'sanctions',
            'status': 'clear',
        })
        partner._compute_sanctions_status()
        self.assertEqual(partner.sanctions_status, 'clear')

        # Create match screening
        self.Screening.create({
            'partner_id': partner.id,
            'screening_type': 'sanctions',
            'status': 'match',
        })
        partner._compute_sanctions_status()
        self.assertEqual(partner.sanctions_status, 'match')
