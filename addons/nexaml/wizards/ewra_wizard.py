# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

"""5-Step EWRA Wizard - Matching nex-systems workflow exactly."""

import logging
import json
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class EwraWizard(models.TransientModel):
    """5-Step EWRA Wizard - Guided workflow matching nex-systems."""
    _name = 'nexaml.ewra.wizard'
    _description = '5-Step EWRA Wizard'

    # ==================== Step Tracking ====================
    current_step = fields.Integer(
        string='Current Step',
        default=1,
        help='Current wizard step (1-5)'
    )

    # ==================== Step 1: View Data & Period ====================
    period_start = fields.Date(
        string='Period Start',
        required=True,
        default=lambda self: fields.Date.today() - timedelta(days=365),
        help='Assessment period start date'
    )
    period_end = fields.Date(
        string='Period End',
        required=True,
        default=fields.Date.today,
        help='Assessment period end date'
    )

    # Preview data (computed)
    preview_data = fields.Text(
        string='Preview Data (JSON)',
        compute='_compute_preview_data',
        help='Stores preview statistics as JSON'
    )
    total_customers = fields.Integer(
        string='Total Customers',
        compute='_compute_preview_stats',
        store=False
    )
    pep_count = fields.Integer(
        string='PEP Count',
        compute='_compute_preview_stats',
        store=False
    )
    high_risk_count = fields.Integer(
        string='High Risk Customers',
        compute='_compute_preview_stats',
        store=False
    )

    # Preview fields for Step 1 display
    preview_customer_low = fields.Integer(string='Low Risk', compute='_compute_preview_stats')
    preview_customer_medium = fields.Integer(string='Medium Risk', compute='_compute_preview_stats')
    preview_customer_high = fields.Integer(string='High Risk', compute='_compute_preview_stats')

    preview_pep_none = fields.Integer(string='Non-PEP', compute='_compute_preview_stats')
    preview_pep_domestic = fields.Integer(string='Domestic PEP', compute='_compute_preview_stats')
    preview_pep_foreign = fields.Integer(string='Foreign PEP', compute='_compute_preview_stats')
    preview_pep_international = fields.Integer(string='International Org PEP', compute='_compute_preview_stats')

    preview_geography_low = fields.Integer(string='Low Risk', compute='_compute_preview_stats')
    preview_geography_medium = fields.Integer(string='Medium Risk', compute='_compute_preview_stats')
    preview_geography_high = fields.Integer(string='High Risk', compute='_compute_preview_stats')

    preview_resident = fields.Integer(string='Resident', compute='_compute_preview_stats')
    preview_non_resident = fields.Integer(string='Non-Resident', compute='_compute_preview_stats')

    preview_products_low = fields.Integer(string='Low Risk', compute='_compute_preview_stats')
    preview_products_medium = fields.Integer(string='Medium Risk', compute='_compute_preview_stats')
    preview_products_high = fields.Integer(string='High Risk', compute='_compute_preview_stats')

    preview_delivery_low = fields.Integer(string='Low Risk', compute='_compute_preview_stats')
    preview_delivery_medium = fields.Integer(string='Medium Risk', compute='_compute_preview_stats')
    preview_delivery_high = fields.Integer(string='High Risk', compute='_compute_preview_stats')

    # ==================== Step 2: Review Inherent Risk ====================
    # (Computed automatically, no user input)
    step2_viewed = fields.Boolean(
        string='Step 2 Viewed',
        default=False,
        help='Track if user has viewed inherent risk'
    )

    # ==================== Step 3: Control Configuration ====================
    wizard_pillar_ids = fields.One2many(
        'nexaml.ewra.wizard.pillar',
        'wizard_id',
        string='Wizard Pillars',
        help='Transient pillar records for editing'
    )

    # ==================== Step 4: Review Residual Risk ====================
    # (Computed from Step 3, no user input)
    step4_viewed = fields.Boolean(
        string='Step 4 Viewed',
        default=False
    )

    # Step 2 computed fields (from wizard_pillar_ids)
    computed_overall_inherent = fields.Float(string='Overall Inherent Risk', compute='_compute_pillar_aggregates')
    computed_overall_inherent_label = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], compute='_compute_pillar_aggregates')

    customer_inherent_score = fields.Float(compute='_compute_pillar_aggregates')
    customer_inherent_label = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], compute='_compute_pillar_aggregates')
    customer_low_pct = fields.Float(compute='_compute_pillar_aggregates')
    customer_medium_pct = fields.Float(compute='_compute_pillar_aggregates')
    customer_high_pct = fields.Float(compute='_compute_pillar_aggregates')

    geography_inherent_score = fields.Float(compute='_compute_pillar_aggregates')
    geography_inherent_label = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], compute='_compute_pillar_aggregates')
    geography_low_pct = fields.Float(compute='_compute_pillar_aggregates')
    geography_medium_pct = fields.Float(compute='_compute_pillar_aggregates')
    geography_high_pct = fields.Float(compute='_compute_pillar_aggregates')

    products_inherent_score = fields.Float(compute='_compute_pillar_aggregates')
    products_inherent_label = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], compute='_compute_pillar_aggregates')
    products_low_pct = fields.Float(compute='_compute_pillar_aggregates')
    products_medium_pct = fields.Float(compute='_compute_pillar_aggregates')
    products_high_pct = fields.Float(compute='_compute_pillar_aggregates')

    delivery_inherent_score = fields.Float(compute='_compute_pillar_aggregates')
    delivery_inherent_label = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], compute='_compute_pillar_aggregates')
    delivery_low_pct = fields.Float(compute='_compute_pillar_aggregates')
    delivery_medium_pct = fields.Float(compute='_compute_pillar_aggregates')
    delivery_high_pct = fields.Float(compute='_compute_pillar_aggregates')

    supplier_inherent_score = fields.Float(compute='_compute_pillar_aggregates')
    supplier_inherent_label = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], compute='_compute_pillar_aggregates')
    supplier_low_pct = fields.Float(compute='_compute_pillar_aggregates')
    supplier_medium_pct = fields.Float(compute='_compute_pillar_aggregates')
    supplier_high_pct = fields.Float(compute='_compute_pillar_aggregates')

    # Step 4 computed fields
    computed_overall_residual = fields.Float(string='Overall Residual Risk', compute='_compute_pillar_aggregates')
    computed_overall_residual_label = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], compute='_compute_pillar_aggregates')
    risk_reduction = fields.Float(string='Risk Reduction %', compute='_compute_pillar_aggregates')

    customer_control_pct = fields.Float(compute='_compute_pillar_aggregates')
    customer_residual_score = fields.Float(compute='_compute_pillar_aggregates')

    geography_control_pct = fields.Float(compute='_compute_pillar_aggregates')
    geography_residual_score = fields.Float(compute='_compute_pillar_aggregates')

    products_control_pct = fields.Float(compute='_compute_pillar_aggregates')
    products_residual_score = fields.Float(compute='_compute_pillar_aggregates')

    delivery_control_pct = fields.Float(compute='_compute_pillar_aggregates')
    delivery_residual_score = fields.Float(compute='_compute_pillar_aggregates')

    supplier_control_pct = fields.Float(compute='_compute_pillar_aggregates')
    supplier_residual_score = fields.Float(compute='_compute_pillar_aggregates')

    # ==================== Step 5: Generate Report ====================
    generated_run_id = fields.Many2one(
        'nexaml.ewra.run',
        string='Generated EWRA Run',
        help='Created run after successful generation'
    )

    # ==================== Settings (applies to all steps) ====================
    use_custom_settings = fields.Boolean(
        string='Use Custom Settings',
        default=False
    )
    custom_risk_threshold_medium = fields.Float(
        string='Medium Risk Threshold',
        default=1.7
    )
    custom_risk_threshold_high = fields.Float(
        string='High Risk Threshold',
        default=2.4
    )
    custom_downgrade_threshold = fields.Integer(
        string='Downgrade Threshold %',
        default=35
    )
    custom_cap_pct = fields.Integer(
        string='Control Cap %',
        default=70
    )
    custom_default_control_band = fields.Selection(
        [('weak', 'Weak (30%)'),
         ('adequate', 'Adequate (60%)'),
         ('strong', 'Strong (80%)'),
         ('very_strong', 'Very Strong (90%)')],
        string='Default Control Band',
        default='adequate'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    include_supplier_pillar = fields.Boolean(
        string='Include Supplier Risk Pillar',
        default=False,
        help='Include supplier risk as a separate pillar (excluded from overall calculation)'
    )

    # ==================== Computed Fields ====================

    @api.depends('period_start', 'period_end')
    def _compute_preview_data(self):
        """Compute preview data for Step 1."""
        for wizard in self:
            if not wizard.period_start or not wizard.period_end:
                wizard.preview_data = '{}'
                continue

            # Get customers
            partners = self.env['res.partner'].search([
                ('customer_rank', '>', 0),
                ('is_company', '=', True)
            ])

            # Build preview data structure
            preview = {
                'total_customers': len(partners),
                'pep_count': len(partners.filtered(lambda p: p.pep_status)),
                'high_risk_count': len(partners.filtered(lambda p: p.risk_level == 'high')),
                'medium_risk_count': len(partners.filtered(lambda p: p.risk_level == 'medium')),
                'low_risk_count': len(partners.filtered(lambda p: p.risk_level == 'low')),

                # Risk distribution by pillar
                'customer_risk': self._get_risk_distribution(partners, 'risk_level'),
                'geography_risk': self._get_numeric_risk_distribution(partners, 'geography_risk'),
                'products_risk': self._get_numeric_risk_distribution(partners, 'product_risk'),
                'delivery_risk': self._get_numeric_risk_distribution(partners, 'channel_risk'),

                # PEP distribution
                'pep_distribution': {
                    'pep': len(partners.filtered(lambda p: p.pep_status)),
                    'non_pep': len(partners.filtered(lambda p: not p.pep_status)),
                },

                # Residency distribution
                'residency_distribution': self._get_residency_distribution(partners),

                # Geography breakdown
                'geography_breakdown': self._get_geography_breakdown(partners),
            }

            wizard.preview_data = json.dumps(preview)

    @api.depends('preview_data')
    def _compute_preview_stats(self):
        """Extract key stats from preview data."""
        for wizard in self:
            try:
                data = json.loads(wizard.preview_data or '{}')
                total = data.get('total_customers', 0)

                wizard.total_customers = total
                wizard.pep_count = data.get('pep_count', 0)
                wizard.high_risk_count = data.get('high_risk_count', 0)

                # Customer risk distribution (counts)
                customer_risk = data.get('customer_risk', {})
                wizard.preview_customer_low = int(customer_risk.get('low', 0) * total / 100) if total > 0 else 0
                wizard.preview_customer_medium = int(customer_risk.get('medium', 0) * total / 100) if total > 0 else 0
                wizard.preview_customer_high = int(customer_risk.get('high', 0) * total / 100) if total > 0 else 0

                # PEP distribution
                pep_dist = data.get('pep_distribution', {})
                wizard.preview_pep_none = pep_dist.get('non_pep', 0)
                wizard.preview_pep_domestic = 0  # TODO: Add if partner model has this field
                wizard.preview_pep_foreign = 0
                wizard.preview_pep_international = 0

                # Geography risk
                geography_risk = data.get('geography_risk', {})
                wizard.preview_geography_low = int(geography_risk.get('low', 0) * total / 100) if total > 0 else 0
                wizard.preview_geography_medium = int(geography_risk.get('medium', 0) * total / 100) if total > 0 else 0
                wizard.preview_geography_high = int(geography_risk.get('high', 0) * total / 100) if total > 0 else 0

                # Residency
                residency = data.get('residency_distribution', {})
                wizard.preview_resident = residency.get('resident', 0)
                wizard.preview_non_resident = residency.get('non_resident', 0)

                # Products risk
                products_risk = data.get('products_risk', {})
                wizard.preview_products_low = int(products_risk.get('low', 0) * total / 100) if total > 0 else 0
                wizard.preview_products_medium = int(products_risk.get('medium', 0) * total / 100) if total > 0 else 0
                wizard.preview_products_high = int(products_risk.get('high', 0) * total / 100) if total > 0 else 0

                # Delivery risk
                delivery_risk = data.get('delivery_risk', {})
                wizard.preview_delivery_low = int(delivery_risk.get('low', 0) * total / 100) if total > 0 else 0
                wizard.preview_delivery_medium = int(delivery_risk.get('medium', 0) * total / 100) if total > 0 else 0
                wizard.preview_delivery_high = int(delivery_risk.get('high', 0) * total / 100) if total > 0 else 0

            except Exception as e:
                _logger.warning(f"Error computing preview stats: {e}")
                wizard.total_customers = 0
                wizard.pep_count = 0
                wizard.high_risk_count = 0
                wizard.preview_customer_low = 0
                wizard.preview_customer_medium = 0
                wizard.preview_customer_high = 0
                wizard.preview_pep_none = 0
                wizard.preview_pep_domestic = 0
                wizard.preview_pep_foreign = 0
                wizard.preview_pep_international = 0
                wizard.preview_geography_low = 0
                wizard.preview_geography_medium = 0
                wizard.preview_geography_high = 0
                wizard.preview_resident = 0
                wizard.preview_non_resident = 0
                wizard.preview_products_low = 0
                wizard.preview_products_medium = 0
                wizard.preview_products_high = 0
                wizard.preview_delivery_low = 0
                wizard.preview_delivery_medium = 0
                wizard.preview_delivery_high = 0

    @api.depends('wizard_pillar_ids.inherent_score', 'wizard_pillar_ids.residual_score',
                 'wizard_pillar_ids.control_pct', 'wizard_pillar_ids.low_pct',
                 'wizard_pillar_ids.medium_pct', 'wizard_pillar_ids.high_pct',
                 'custom_risk_threshold_medium', 'custom_risk_threshold_high')
    def _compute_pillar_aggregates(self):
        """Compute all aggregated risk values from wizard pillars."""
        for wizard in self:
            pillars = wizard.wizard_pillar_ids

            # Helper to get pillar by type
            def get_pillar(pillar_type):
                return pillars.filtered(lambda p: p.pillar == pillar_type)[:1]

            # Helper to get risk label
            def get_label(score):
                medium_thresh = wizard.custom_risk_threshold_medium or 1.7
                high_thresh = wizard.custom_risk_threshold_high or 2.4
                if score >= high_thresh:
                    return 'high'
                elif score >= medium_thresh:
                    return 'medium'
                else:
                    return 'low'

            # Customer pillar
            customer = get_pillar('customer')
            wizard.customer_inherent_score = customer.inherent_score if customer else 0.0
            wizard.customer_inherent_label = get_label(customer.inherent_score) if customer else 'low'
            wizard.customer_low_pct = customer.low_pct if customer else 0.0
            wizard.customer_medium_pct = customer.medium_pct if customer else 0.0
            wizard.customer_high_pct = customer.high_pct if customer else 0.0
            wizard.customer_control_pct = customer.control_pct if customer else 0.0
            wizard.customer_residual_score = customer.residual_score if customer else 0.0

            # Geography pillar
            geography = get_pillar('geography')
            wizard.geography_inherent_score = geography.inherent_score if geography else 0.0
            wizard.geography_inherent_label = get_label(geography.inherent_score) if geography else 'low'
            wizard.geography_low_pct = geography.low_pct if geography else 0.0
            wizard.geography_medium_pct = geography.medium_pct if geography else 0.0
            wizard.geography_high_pct = geography.high_pct if geography else 0.0
            wizard.geography_control_pct = geography.control_pct if geography else 0.0
            wizard.geography_residual_score = geography.residual_score if geography else 0.0

            # Products pillar
            products = get_pillar('products')
            wizard.products_inherent_score = products.inherent_score if products else 0.0
            wizard.products_inherent_label = get_label(products.inherent_score) if products else 'low'
            wizard.products_low_pct = products.low_pct if products else 0.0
            wizard.products_medium_pct = products.medium_pct if products else 0.0
            wizard.products_high_pct = products.high_pct if products else 0.0
            wizard.products_control_pct = products.control_pct if products else 0.0
            wizard.products_residual_score = products.residual_score if products else 0.0

            # Delivery pillar
            delivery = get_pillar('delivery')
            wizard.delivery_inherent_score = delivery.inherent_score if delivery else 0.0
            wizard.delivery_inherent_label = get_label(delivery.inherent_score) if delivery else 'low'
            wizard.delivery_low_pct = delivery.low_pct if delivery else 0.0
            wizard.delivery_medium_pct = delivery.medium_pct if delivery else 0.0
            wizard.delivery_high_pct = delivery.high_pct if delivery else 0.0
            wizard.delivery_control_pct = delivery.control_pct if delivery else 0.0
            wizard.delivery_residual_score = delivery.residual_score if delivery else 0.0

            # Supplier pillar (optional)
            supplier = get_pillar('supplier')
            wizard.supplier_inherent_score = supplier.inherent_score if supplier else 0.0
            wizard.supplier_inherent_label = get_label(supplier.inherent_score) if supplier else 'low'
            wizard.supplier_low_pct = supplier.low_pct if supplier else 0.0
            wizard.supplier_medium_pct = supplier.medium_pct if supplier else 0.0
            wizard.supplier_high_pct = supplier.high_pct if supplier else 0.0
            wizard.supplier_control_pct = supplier.control_pct if supplier else 0.0
            wizard.supplier_residual_score = supplier.residual_score if supplier else 0.0

            # Overall weighted inherent risk (Customer:40%, Products:25%, Geography:20%, Delivery:15%)
            pillar_weights = {
                'customer': 0.4,
                'geography': 0.2,
                'products': 0.25,
                'delivery': 0.15,
                'supplier': 0
            }

            core_pillars = pillars.filtered(lambda p: p.pillar != 'supplier')
            total_weight = sum([pillar_weights.get(p.pillar, 0) for p in core_pillars])

            if total_weight > 0:
                weighted_inherent_sum = sum([
                    p.inherent_score * pillar_weights.get(p.pillar, 0)
                    for p in core_pillars
                ])
                wizard.computed_overall_inherent = weighted_inherent_sum / total_weight
                wizard.computed_overall_inherent_label = get_label(wizard.computed_overall_inherent)

                weighted_residual_sum = sum([
                    p.residual_score * pillar_weights.get(p.pillar, 0)
                    for p in core_pillars
                ])
                wizard.computed_overall_residual = weighted_residual_sum / total_weight
                wizard.computed_overall_residual_label = get_label(wizard.computed_overall_residual)

                # Risk reduction
                if wizard.computed_overall_inherent > 0:
                    wizard.risk_reduction = ((wizard.computed_overall_inherent - wizard.computed_overall_residual) / wizard.computed_overall_inherent) * 100
                else:
                    wizard.risk_reduction = 0.0
            else:
                wizard.computed_overall_inherent = 0.0
                wizard.computed_overall_inherent_label = 'low'
                wizard.computed_overall_residual = 0.0
                wizard.computed_overall_residual_label = 'low'
                wizard.risk_reduction = 0.0

    # ==================== Helper Methods ====================

    def _get_risk_distribution(self, partners, field_name):
        """Get risk distribution for selection field."""
        total = len(partners)
        if total == 0:
            return {'low': 0, 'medium': 0, 'high': 0}

        low = len(partners.filtered(lambda p: p[field_name] == 'low'))
        medium = len(partners.filtered(lambda p: p[field_name] == 'medium'))
        high = len(partners.filtered(lambda p: p[field_name] == 'high'))

        return {
            'low': round(low / total * 100, 1),
            'medium': round(medium / total * 100, 1),
            'high': round(high / total * 100, 1),
        }

    def _get_numeric_risk_distribution(self, partners, field_name):
        """Get risk distribution for numeric risk field."""
        total = len(partners)
        if total == 0:
            return {'low': 0, 'medium': 0, 'high': 0}

        low = len(partners.filtered(lambda p: p[field_name] < 1.7))
        medium = len(partners.filtered(lambda p: 1.7 <= p[field_name] < 2.4))
        high = len(partners.filtered(lambda p: p[field_name] >= 2.4))

        return {
            'low': round(low / total * 100, 1),
            'medium': round(medium / total * 100, 1),
            'high': round(high / total * 100, 1),
        }

    def _get_residency_distribution(self, partners):
        """Get residency distribution."""
        total = len(partners)
        if total == 0:
            return {}

        countries = {}
        for partner in partners:
            country = partner.country_id.name or 'Unknown'
            countries[country] = countries.get(country, 0) + 1

        # Convert to percentages and sort
        return {
            country: round(count / total * 100, 1)
            for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]
        }

    def _get_geography_breakdown(self, partners):
        """Get detailed geography breakdown."""
        total = len(partners)
        if total == 0:
            return []

        countries = {}
        for partner in partners:
            country = partner.country_id.name or 'Unknown'
            if country not in countries:
                countries[country] = {'count': 0, 'high_risk': 0}
            countries[country]['count'] += 1
            if partner.geography_risk >= 2.4:
                countries[country]['high_risk'] += 1

        result = []
        for country, data in sorted(countries.items(), key=lambda x: x[1]['count'], reverse=True)[:10]:
            result.append({
                'country': country,
                'count': data['count'],
                'percentage': round(data['count'] / total * 100, 1),
                'high_risk': data['high_risk'],
            })

        return result

    # ==================== Navigation Methods ====================

    def action_next_step(self):
        """Navigate to next step."""
        self.ensure_one()

        # Validation before moving to next step
        if self.current_step == 1:
            self._validate_step1()
            # Initialize wizard pillars for step 3
            self._initialize_wizard_pillars()
        elif self.current_step == 2:
            self.step2_viewed = True
        elif self.current_step == 3:
            self._validate_step3()
        elif self.current_step == 4:
            self.step4_viewed = True

        # Move to next step
        self.current_step = min(self.current_step + 1, 5)

        return self._reopen_wizard()

    def action_previous_step(self):
        """Navigate to previous step."""
        self.ensure_one()
        self.current_step = max(self.current_step - 1, 1)
        return self._reopen_wizard()

    def _reopen_wizard(self):
        """Reopen wizard at current step."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('EWRA Wizard - Step %s of 5') % self.current_step,
            'res_model': 'nexaml.ewra.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_current_step': self.current_step},
        }

    # ==================== Validation Methods ====================

    @api.constrains('period_start', 'period_end')
    def _check_period_dates(self):
        """Validate period dates."""
        for wizard in self:
            if wizard.period_start > wizard.period_end:
                raise ValidationError(_('Period start date must be before end date.'))

    def _validate_step1(self):
        """Validate Step 1 inputs."""
        self.ensure_one()
        if not self.period_start or not self.period_end:
            raise ValidationError(_('Please select both start and end dates.'))
        if self.period_start > self.period_end:
            raise ValidationError(_('Start date must be before end date.'))

    def _validate_step3(self):
        """Validate Step 3 control configuration."""
        self.ensure_one()
        for pillar in self.wizard_pillar_ids:
            total = pillar.low_pct + pillar.medium_pct + pillar.high_pct
            if abs(total - 100.0) > 0.1:
                raise ValidationError(
                    _('Pillar %s: percentages must sum to 100%% (currently %.1f%%)') % (
                        pillar.get_pillar_display_name(), total
                    )
                )

    # ==================== Pillar Initialization ====================

    def _initialize_wizard_pillars(self):
        """Initialize wizard pillars for Step 3 based on preview data."""
        self.ensure_one()

        # Clear existing wizard pillars
        self.wizard_pillar_ids.unlink()

        # Get preview data
        try:
            preview = json.loads(self.preview_data or '{}')
        except:
            preview = {}

        # Create wizard pillars with auto-populated distributions
        pillars_data = [
            ('customer', 10, preview.get('customer_risk', {})),
            ('geography', 20, preview.get('geography_risk', {})),
            ('products', 30, preview.get('products_risk', {})),
            ('delivery', 40, preview.get('delivery_risk', {})),
        ]

        for pillar_type, sequence, distribution in pillars_data:
            low_pct = distribution.get('low', 60.0)
            medium_pct = distribution.get('medium', 30.0)
            high_pct = distribution.get('high', 10.0)

            # Normalize to ensure sum = 100
            total = low_pct + medium_pct + high_pct
            if total > 0:
                low_pct = round(low_pct / total * 100, 1)
                medium_pct = round(medium_pct / total * 100, 1)
                high_pct = round(100 - low_pct - medium_pct, 1)  # Ensure exact 100

            self.env['nexaml.ewra.wizard.pillar'].create({
                'wizard_id': self.id,
                'pillar': pillar_type,
                'sequence': sequence,
                'low_pct': low_pct,
                'medium_pct': medium_pct,
                'high_pct': high_pct,
                'control_band': self.custom_default_control_band or 'adequate',
            })

    # ==================== Final EWRA Generation ====================

    def action_generate_ewra(self):
        """Generate final EWRA run from wizard (Step 5)."""
        self.ensure_one()

        # Create EWRA run
        ewra_run = self.env['nexaml.ewra.run'].create({
            'period_start': self.period_start,
            'period_end': self.period_end,
            'company_id': self.company_id.id,
            'status': 'in_progress',
        })

        # Create settings snapshot
        if self.use_custom_settings:
            snapshot = self.env['nexaml.ewra.settings.snapshot'].create({
                'run_id': ewra_run.id,
                'risk_threshold_medium': self.custom_risk_threshold_medium,
                'risk_threshold_high': self.custom_risk_threshold_high,
                'downgrade_threshold': self.custom_downgrade_threshold,
                'cap_pct': self.custom_cap_pct,
                'default_control_band': self.custom_default_control_band,
            })
        else:
            snapshot = self.env['nexaml.ewra.settings.snapshot'].create_from_current_settings(ewra_run.id)

        ewra_run.settings_snapshot_id = snapshot.id

        # Create pillars from wizard pillars
        for wizard_pillar in self.wizard_pillar_ids:
            self.env['nexaml.ewra.pillar'].create({
                'run_id': ewra_run.id,
                'pillar': wizard_pillar.pillar,
                'sequence': wizard_pillar.sequence,
                'low_pct': wizard_pillar.low_pct,
                'medium_pct': wizard_pillar.medium_pct,
                'high_pct': wizard_pillar.high_pct,
                'control_band': wizard_pillar.control_band,
                'custom_control_pct': wizard_pillar.custom_control_pct,
                'control_reason': wizard_pillar.control_reason,
                'notes': wizard_pillar.notes,
            })

        # Create default narrative
        narrative = self.env['nexaml.ewra.narrative'].create({
            'run_id': ewra_run.id,
        })
        ewra_run.narrative_id = narrative.id

        self.generated_run_id = ewra_run.id

        # Return action to open the created EWRA run
        return {
            'type': 'ir.actions.act_window',
            'name': _('EWRA Assessment'),
            'res_model': 'nexaml.ewra.run',
            'res_id': ewra_run.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_generated_run(self):
        """Open the generated EWRA run record."""
        self.ensure_one()
        if not self.generated_run_id:
            raise ValidationError(_('No EWRA run has been generated yet.'))

        return {
            'type': 'ir.actions.act_window',
            'name': _('EWRA Assessment'),
            'res_model': 'nexaml.ewra.run',
            'res_id': self.generated_run_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class EwraWizardPillar(models.TransientModel):
    """Transient pillar model for Step 3 editing."""
    _name = 'nexaml.ewra.wizard.pillar'
    _description = 'EWRA Wizard Pillar'
    _order = 'sequence, id'

    wizard_id = fields.Many2one(
        'nexaml.ewra.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    pillar = fields.Selection(
        [('customer', 'Customer Risk'),
         ('geography', 'Geography Risk'),
         ('products', 'Products & Services Risk'),
         ('delivery', 'Delivery Channel Risk'),
         ('supplier', 'Supplier Risk')],
        string='Pillar Type',
        required=True
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )

    # Risk Distribution (must sum to 100%)
    low_pct = fields.Float(
        string='Low %',
        required=True,
        default=60.0,
        help='Percentage of low-risk entities (1.0-1.6)'
    )
    medium_pct = fields.Float(
        string='Medium %',
        required=True,
        default=30.0,
        help='Percentage of medium-risk entities (1.7-2.3)'
    )
    high_pct = fields.Float(
        string='High %',
        required=True,
        default=10.0,
        help='Percentage of high-risk entities (2.4-3.0)'
    )

    # Computed: Inherent Risk
    inherent_score = fields.Float(
        string='Inherent Risk Score',
        compute='_compute_inherent_score',
        store=False,
        help='Calculated: (low% × 1 + med% × 2 + high% × 3) / 100'
    )
    inherent_label = fields.Selection(
        [('low', 'Low'),
         ('medium', 'Medium'),
         ('high', 'High')],
        string='Inherent Risk Level',
        compute='_compute_inherent_score',
        store=False
    )

    # Control Configuration
    control_band = fields.Selection(
        [('weak', 'Weak (30%)'),
         ('adequate', 'Adequate (60%)'),
         ('strong', 'Strong (80%)'),
         ('very_strong', 'Very Strong (90%)'),
         ('custom', 'Custom')],
        string='Control Band',
        required=True,
        default='adequate',
        help='Control effectiveness band'
    )
    custom_control_pct = fields.Float(
        string='Custom Control %',
        help='Custom control percentage (0-100%)'
    )
    control_pct = fields.Float(
        string='Effective Control %',
        compute='_compute_control_pct',
        store=False,
        help='Effective control percentage based on band'
    )
    control_reason = fields.Text(
        string='Control Justification',
        help='Justification for control effectiveness assessment'
    )

    # Computed: Residual Risk
    residual_score = fields.Float(
        string='Residual Risk Score',
        compute='_compute_residual_score',
        store=False,
        help='Calculated: inherent × (1 - control%), min 1.0'
    )
    residual_label = fields.Selection(
        [('low', 'Low'),
         ('medium', 'Medium'),
         ('high', 'High')],
        string='Residual Risk Level',
        compute='_compute_residual_score',
        store=False
    )

    notes = fields.Text(
        string='Notes',
        help='Additional notes for this pillar'
    )

    @api.depends('low_pct', 'medium_pct', 'high_pct')
    def _compute_inherent_score(self):
        """Compute inherent risk score and label."""
        for pillar in self:
            low = pillar.low_pct or 0.0
            medium = pillar.medium_pct or 0.0
            high = pillar.high_pct or 0.0

            pillar.inherent_score = ((low * 1.0) + (medium * 2.0) + (high * 3.0)) / 100.0

            # Classify
            if pillar.inherent_score < 1.7:
                pillar.inherent_label = 'low'
            elif pillar.inherent_score < 2.4:
                pillar.inherent_label = 'medium'
            else:
                pillar.inherent_label = 'high'

    @api.depends('control_band', 'custom_control_pct')
    def _compute_control_pct(self):
        """Compute effective control percentage."""
        for pillar in self:
            if pillar.control_band == 'custom':
                pillar.control_pct = pillar.custom_control_pct or 0.0
            elif pillar.control_band == 'weak':
                pillar.control_pct = 30.0
            elif pillar.control_band == 'adequate':
                pillar.control_pct = 60.0
            elif pillar.control_band == 'strong':
                pillar.control_pct = 80.0
            elif pillar.control_band == 'very_strong':
                pillar.control_pct = 90.0
            else:
                pillar.control_pct = 0.0

    @api.depends('inherent_score', 'control_pct')
    def _compute_residual_score(self):
        """Compute residual risk score and label."""
        for pillar in self:
            control_pct = pillar.control_pct or 0.0
            inherent = pillar.inherent_score
            control = control_pct / 100.0

            # Apply control effectiveness (min 1.0)
            pillar.residual_score = max(1.0, inherent * (1 - control))

            # Classify
            if pillar.residual_score < 1.7:
                pillar.residual_label = 'low'
            elif pillar.residual_score < 2.4:
                pillar.residual_label = 'medium'
            else:
                pillar.residual_label = 'high'

    def get_pillar_display_name(self):
        """Get display name for pillar."""
        self.ensure_one()
        pillar_names = dict(self._fields['pillar'].selection)
        return pillar_names.get(self.pillar, self.pillar)

    @api.constrains('low_pct', 'medium_pct', 'high_pct')
    def _check_percentages_sum(self):
        """Validate that percentages sum to 100%."""
        for pillar in self:
            total = pillar.low_pct + pillar.medium_pct + pillar.high_pct
            if abs(total - 100.0) > 0.1:  # Allow 0.1% tolerance for rounding
                raise ValidationError(
                    _('Pillar %s: Low, Medium, and High percentages must sum to 100%% (currently %.1f%%)') % (
                        pillar.get_pillar_display_name(), total
                    )
                )
