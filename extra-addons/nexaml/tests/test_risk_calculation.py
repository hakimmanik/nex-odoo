# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'nexaml')
class TestRiskCalculation(TransactionCase):
    """Test customer risk assessment calculations."""

    def setUp(self):
        super().setUp()
        self.Partner = self.env['res.partner']
        self.Product = self.env['product.template']
        self.Control = self.env['aml.control']

        # Create test products
        self.low_risk_product = self.Product.create({
            'name': 'Low Risk Product',
            'risk_score': '1',
        })
        self.high_risk_product = self.Product.create({
            'name': 'High Risk Product',
            'risk_score': '3',
        })

        # Create test control
        self.control = self.Control.create({
            'name': 'Enhanced Monitoring',
            'mitigation_factor': 0.7,
        })

    def test_inherent_risk_calculation(self):
        """Test inherent risk calculation with weighted formula."""
        partner = self.Partner.create({
            'name': 'Test Customer',
            'customer_risk': '2',
            'geography_risk': '2',
            'product_risk': '2',
            'channel_risk': '2',
        })

        # Formula: (2*0.30) + (2*0.20) + (2*0.30) + (2*0.20) = 2.0
        self.assertEqual(partner.inherent_risk, 2.0)

    def test_residual_risk_with_controls(self):
        """Test residual risk calculation with controls applied."""
        partner = self.Partner.create({
            'name': 'Test Customer',
            'customer_risk': '3',
            'geography_risk': '3',
            'product_risk': '3',
            'channel_risk': '3',
            'control_ids': [(6, 0, [self.control.id])],
        })

        # Inherent: (3*0.30) + (3*0.20) + (3*0.30) + (3*0.20) = 3.0
        self.assertEqual(partner.inherent_risk, 3.0)

        # Residual: 3.0 * 0.7 = 2.1
        self.assertEqual(partner.residual_risk, 2.1)

    def test_risk_level_classification(self):
        """Test risk level assignment based on residual risk."""
        # Low risk (< 1.7)
        low_partner = self.Partner.create({
            'name': 'Low Risk Customer',
            'customer_risk': '1',
            'geography_risk': '1',
            'product_risk': '1',
            'channel_risk': '1',
        })
        self.assertEqual(low_partner.risk_level, 'low')

        # Medium risk (1.7-2.3)
        medium_partner = self.Partner.create({
            'name': 'Medium Risk Customer',
            'customer_risk': '2',
            'geography_risk': '2',
            'product_risk': '2',
            'channel_risk': '2',
        })
        self.assertEqual(medium_partner.risk_level, 'medium')

        # High risk (>= 2.4)
        high_partner = self.Partner.create({
            'name': 'High Risk Customer',
            'customer_risk': '3',
            'geography_risk': '3',
            'product_risk': '3',
            'channel_risk': '3',
        })
        self.assertEqual(high_partner.risk_level, 'high')

    def test_edd_requirement(self):
        """Test EDD requirement flag based on risk level."""
        # Configure EDD threshold to medium
        self.env['ir.config_parameter'].sudo().set_param('nexaml.edd_threshold', 'medium')

        high_partner = self.Partner.create({
            'name': 'High Risk Customer',
            'customer_risk': '3',
            'geography_risk': '3',
            'product_risk': '3',
            'channel_risk': '3',
        })

        self.assertTrue(high_partner.edd_required)

    def test_product_risk_integration(self):
        """Test product risk integration in overall risk."""
        partner = self.Partner.create({
            'name': 'Test Customer',
            'customer_risk': '1',
            'geography_risk': '1',
            'channel_risk': '1',
            'product_ids': [(6, 0, [self.high_risk_product.id])],
        })

        # Product risk should be computed from products
        partner._compute_product_risk()
        self.assertEqual(partner.product_risk, '3')

    def test_multiple_controls_use_best(self):
        """Test that multiple controls use the best (lowest) mitigation factor."""
        control1 = self.Control.create({
            'name': 'Control 1',
            'mitigation_factor': 0.8,
        })
        control2 = self.Control.create({
            'name': 'Control 2',
            'mitigation_factor': 0.6,
        })

        partner = self.Partner.create({
            'name': 'Test Customer',
            'customer_risk': '2',
            'geography_risk': '2',
            'product_risk': '2',
            'channel_risk': '2',
            'control_ids': [(6, 0, [control1.id, control2.id])],
        })

        # Should use 0.6 (best control)
        # Inherent: 2.0, Residual: 2.0 * 0.6 = 1.2
        self.assertEqual(partner.residual_risk, 1.2)
