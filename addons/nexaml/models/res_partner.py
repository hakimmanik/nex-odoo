# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import requests
import json
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """Extend partner with AML risk assessment fields."""
    _inherit = 'res.partner'

    # Risk Assessment Fields
    risk_level = fields.Selection(
        [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        string='Risk Level',
        compute='_compute_risk',
        store=True,
        help='Overall risk level: Low (1.0-1.6), Medium (1.7-2.3), High (2.4-3.0)'
    )
    inherent_risk = fields.Float(
        string='Inherent Risk Score',
        compute='_compute_risk',
        store=True,
        help='Calculated inherent risk before controls (1.0-3.0)'
    )
    residual_risk = fields.Float(
        string='Residual Risk Score',
        compute='_compute_risk',
        store=True,
        help='Risk after applying controls'
    )
    last_assessment_date = fields.Date(
        string='Last Assessment Date',
        help='Date of last risk assessment'
    )
    next_review_date = fields.Date(
        string='Next Review Date',
        help='Date when risk assessment should be reviewed'
    )
    pep_status = fields.Boolean(
        string='Politically Exposed Person (PEP)',
        default=False,
        help='Whether customer is a Politically Exposed Person'
    )
    edd_required = fields.Boolean(
        string='Enhanced Due Diligence Required',
        compute='_compute_edd_required',
        store=True,
        help='Whether Enhanced Due Diligence is required based on risk level'
    )
    risk_reasoning = fields.Text(
        string='Risk Assessment Reasoning',
        compute='_compute_risk',
        store=True,
        help='Explanation of how the risk score was calculated'
    )

    # Related Party Fields (for contacts/child partners)
    party_type = fields.Selection(
        [('director', 'Director'),
         ('shareholder', 'Shareholder'),
         ('ubo', 'Ultimate Beneficial Owner'),
         ('signatory', 'Authorized Signatory'),
         ('related', 'Related Person')],
        string='Party Type',
        help='Type of relationship for contacts of legal entities'
    )
    ownership_percentage = fields.Float(
        string='Ownership %',
        help='Ownership percentage for shareholders and UBOs (≥25% for UBO)'
    )
    is_ubo = fields.Boolean(
        string='Is UBO',
        compute='_compute_is_ubo',
        store=True,
        help='Computed: True if ownership ≥ 25%'
    )

    # Risk Factor Fields (Float scores 1.0-3.0)
    customer_risk = fields.Float(
        string='Customer Risk Score',
        compute='_compute_customer_risk',
        store=True,
        help='Customer-specific risk factors (PEP, sanctions, ownership structure, etc.)'
    )
    geography_risk = fields.Float(
        string='Geography Risk Score',
        compute='_compute_geography_risk',
        store=True,
        help='Geographic risk based on country/jurisdiction'
    )
    product_risk = fields.Float(
        string='Product Risk Score',
        compute='_compute_product_risk',
        store=True,
        help='Highest risk level from associated products'
    )
    channel_risk = fields.Float(
        string='Channel Risk Score',
        compute='_compute_channel_risk',
        store=True,
        help='Delivery channel risk (online, face-to-face, etc.)'
    )

    # Risk heatmap bars (HTML)
    customer_risk_bar = fields.Html(
        string='Customer Risk Bar',
        compute='_compute_risk_bars',
        sanitize=False
    )
    geography_risk_bar = fields.Html(
        string='Geography Risk Bar',
        compute='_compute_risk_bars',
        sanitize=False
    )
    product_risk_bar = fields.Html(
        string='Product Risk Bar',
        compute='_compute_risk_bars',
        sanitize=False
    )
    channel_risk_bar = fields.Html(
        string='Channel Risk Bar',
        compute='_compute_risk_bars',
        sanitize=False
    )

    # Relationships
    product_ids = fields.Many2many(
        'product.template',
        'partner_product_rel',
        'partner_id',
        'product_id',
        string='Products',
        help='Products/services used by this customer'
    )
    control_ids = fields.Many2many(
        'aml.control',
        'partner_control_rel',
        'partner_id',
        'control_id',
        string='Controls',
        help='Risk controls applied to this customer'
    )

    # Sanctions Screening Fields
    sanctions_status = fields.Selection(
        [('not_screened', 'Not Screened'),
         ('clear', 'Clear'),
         ('match', 'Match Found'),
         ('false_positive', 'False Positive'),
         ('pending', 'Screening in Progress')],
        string='Sanctions Status',
        default='not_screened',
        help='Current sanctions screening status'
    )
    last_screening_date = fields.Date(
        string='Last Screening Date',
        help='Date of last sanctions screening'
    )
    screening_ids = fields.One2many(
        'aml.screening',
        'partner_id',
        string='Screening History',
        help='All sanctions screening records for this customer'
    )
    screening_count = fields.Integer(
        string='Screening Count',
        compute='_compute_screening_count',
        help='Number of screening records'
    )
    alert_ids = fields.One2many(
        'aml.alert',
        'partner_id',
        string='Alerts',
        help='Alerts related to this customer'
    )
    alert_count = fields.Integer(
        string='Alert Count',
        compute='_compute_alert_count',
        help='Number of active alerts'
    )

    # Employment & Financial Information (for natural persons)
    occupation = fields.Char(
        string='Occupation',
        help='Customer occupation/profession'
    )
    employer_name = fields.Char(
        string='Employer Name',
        help='Name of employer'
    )
    employer_address = fields.Text(
        string='Employer Address',
        help='Address of employer'
    )
    source_of_funds = fields.Selection(
        [('salary', 'Salary/Wages'),
         ('business', 'Business Income'),
         ('investment', 'Investment Income'),
         ('inheritance', 'Inheritance'),
         ('savings', 'Savings'),
         ('pension', 'Pension/Retirement'),
         ('gift', 'Gift/Donation'),
         ('other', 'Other')],
        string='Source of Funds',
        help='Primary source of funds'
    )
    source_of_funds_other = fields.Char(
        string='Other Source',
        help='Specify if source is "Other"'
    )
    annual_income_range = fields.Selection(
        [('0-25k', 'Under $25,000'),
         ('25k-50k', '$25,000 - $50,000'),
         ('50k-100k', '$50,000 - $100,000'),
         ('100k-250k', '$100,000 - $250,000'),
         ('250k-500k', '$250,000 - $500,000'),
         ('500k-1m', '$500,000 - $1,000,000'),
         ('1m+', 'Over $1,000,000')],
        string='Annual Income Range',
        help='Estimated annual income range'
    )

    # Compliance Flags
    kyc_expiry_date = fields.Date(
        string='KYC Expiry Date',
        help='Date when KYC/CDD documentation expires'
    )
    kyc_expired = fields.Boolean(
        string='KYC Expired',
        compute='_compute_kyc_expired',
        store=True,
        help='Whether KYC documentation has expired'
    )
    on_watch_list = fields.Boolean(
        string='On Watch List',
        default=False,
        help='Customer is on internal watch list'
    )
    watch_list_reason = fields.Text(
        string='Watch List Reason',
        help='Reason for watch list placement'
    )

    @api.depends('kyc_expiry_date')
    def _compute_kyc_expired(self):
        """Check if KYC has expired."""
        today = fields.Date.today()
        for partner in self:
            partner.kyc_expired = partner.kyc_expiry_date and partner.kyc_expiry_date < today

    @api.depends('ownership_percentage')
    def _compute_is_ubo(self):
        """Compute if contact is UBO based on ownership percentage."""
        for partner in self:
            partner.is_ubo = partner.ownership_percentage >= 25.0

    @api.depends('screening_ids')
    def _compute_screening_count(self):
        """Count screening records."""
        for partner in self:
            partner.screening_count = len(partner.screening_ids)

    @api.depends('alert_ids')
    def _compute_alert_count(self):
        """Count active alerts (new or investigating)."""
        for partner in self:
            partner.alert_count = len(partner.alert_ids.filtered(
                lambda a: a.status in ('new', 'investigating')
            ))

    @api.depends('customer_risk', 'geography_risk', 'product_risk',
                 'channel_risk', 'control_ids', 'control_ids.mitigation_factor',
                 'pep_status', 'sanctions_status', 'child_ids.pep_status',
                 'child_ids.sanctions_status', 'child_ids.is_ubo')
    def _compute_risk(self):
        """Calculate inherent and residual risk scores with scenario-based overrides."""
        for partner in self:
            # Get risk factors (default to 1 if not set)
            customer_risk = float(partner.customer_risk or '1')
            geography_risk = float(partner.geography_risk or '1')
            product_risk = float(partner.product_risk or '1')
            channel_risk = float(partner.channel_risk or '1')

            # Build reasoning
            reasoning_lines = []
            reasoning_lines.append("=== CUSTOMER RISK ASSESSMENT ===\n")

            # Helper to get risk label from score
            def get_risk_label(score):
                if score < 1.7:
                    return 'Low'
                elif score < 2.4:
                    return 'Medium'
                else:
                    return 'High'

            # Component breakdown
            reasoning_lines.append("Risk Components:")
            reasoning_lines.append(f"  • Customer Risk: {customer_risk:.2f} ({get_risk_label(customer_risk)})")
            reasoning_lines.append(f"  • Geography Risk: {geography_risk:.2f} ({get_risk_label(geography_risk)})")
            reasoning_lines.append(f"  • Product Risk: {product_risk:.2f} ({get_risk_label(product_risk)})")
            reasoning_lines.append(f"  • Channel Risk: {channel_risk:.2f} ({get_risk_label(channel_risk)})\n")

            # Calculate inherent risk using weighted formula
            # (Customer × 0.30) + (Geography × 0.20) + (Product × 0.30) + (Channel × 0.20)
            inherent_risk = (
                (customer_risk * 0.30) +
                (geography_risk * 0.20) +
                (product_risk * 0.30) +
                (channel_risk * 0.20)
            )
            partner.inherent_risk = inherent_risk

            reasoning_lines.append("Inherent Risk Calculation:")
            reasoning_lines.append(f"  ({customer_risk} × 0.30) + ({geography_risk} × 0.20) + ({product_risk} × 0.30) + ({channel_risk} × 0.20)")
            reasoning_lines.append(f"  = {customer_risk * 0.30:.2f} + {geography_risk * 0.20:.2f} + {product_risk * 0.30:.2f} + {channel_risk * 0.20:.2f}")
            reasoning_lines.append(f"  = {inherent_risk:.2f}\n")

            # Calculate residual risk after controls
            residual_risk = inherent_risk
            if partner.control_ids:
                # Apply strongest mitigation (lowest factor)
                min_mitigation = min(partner.control_ids.mapped('mitigation_factor'))
                residual_risk = inherent_risk * min_mitigation
                reasoning_lines.append("Risk Mitigation Controls Applied:")
                for control in partner.control_ids:
                    reasoning_lines.append(f"  • {control.name} (factor: {control.mitigation_factor})")
                reasoning_lines.append(f"  Best mitigation factor: {min_mitigation}")
                reasoning_lines.append(f"  Residual Risk: {inherent_risk:.2f} × {min_mitigation} = {residual_risk:.2f}\n")
            else:
                reasoning_lines.append("No mitigation controls applied.\n")

            partner.residual_risk = residual_risk

            # Scenario-Based Risk Overrides with CRA Settings
            override_high = False
            override_block = False
            override_reason = []

            # Get CRA settings for scenario-based actions
            cra_settings = self.env['nexaml.cra.settings'].get_settings(partner.company_id.id)

            # Override 1: PEP Status (customer or related parties)
            if cra_settings.pep_status_enabled and partner.pep_status:
                if cra_settings.pep_status_action == 'block':
                    override_block = True
                    override_reason.append('Customer is PEP (BLOCKED by policy)')
                else:  # elevate_high
                    override_high = True
                    override_reason.append('Customer is PEP')

            # Check UBOs and related parties for PEP status
            if cra_settings.pep_status_enabled and partner.child_ids:
                pep_contacts = partner.child_ids.filtered(lambda c: c.pep_status and c.is_ubo)
                if pep_contacts:
                    if cra_settings.pep_status_action == 'block':
                        override_block = True
                        override_reason.append('UBO is PEP (BLOCKED by policy)')
                    else:
                        override_high = True
                        override_reason.append('UBO is PEP')

            # Override 2: Confirmed Sanctions Match
            if cra_settings.confirmed_sanctions_enabled and partner.sanctions_status == 'match':
                # Check if confirmed via case decision
                latest_decision = self.env['aml.case.decision'].search([
                    ('case_id.partner_id', '=', partner.id),
                    ('case_id.case_type', 'in', ['sanctions', 'pep', 'adverse_media', 'screening'])
                ], order='decided_date desc', limit=1)

                if latest_decision and latest_decision.outcome in ['true_positive', 'ongoing_monitoring', 'relationship_terminated']:
                    if cra_settings.confirmed_sanctions_action == 'block':
                        override_block = True
                        override_reason.append('Confirmed sanctions match (BLOCKED by policy)')
                    else:
                        override_high = True
                        override_reason.append('Confirmed sanctions match')

            if cra_settings.confirmed_sanctions_enabled and partner.child_ids:
                sanctioned_contacts = partner.child_ids.filtered(
                    lambda c: c.sanctions_status == 'match' and c.is_ubo
                )
                if sanctioned_contacts:
                    if cra_settings.confirmed_sanctions_action == 'block':
                        override_block = True
                        override_reason.append('UBO sanctions match (BLOCKED by policy)')
                    else:
                        override_high = True
                        override_reason.append('UBO sanctions match')

            # Apply block override first (highest priority)
            if override_block:
                partner.risk_level = 'blocked'
                partner.risk_score = 0.0
                partner.residual_risk = 0.0
                partner.residual_risk_score = 0.0
                reasoning_lines.append("🚫 CUSTOMER BLOCKED:")
                for reason in override_reason:
                    reasoning_lines.append(f"  • {reason}")
                reasoning_lines.append("  Customer relationship blocked by policy.\n")
                partner.risk_reasoning = '\n'.join(reasoning_lines)
                _logger.warning('Customer blocked for partner %s: %s',
                              partner.name, ', '.join(override_reason))
                continue

            # Apply override if triggered
            if override_high:
                residual_risk = 3.0  # Force maximum risk
                partner.residual_risk = residual_risk
                reasoning_lines.append("⚠ RISK OVERRIDE - ELEVATED TO HIGH:")
                for reason in override_reason:
                    reasoning_lines.append(f"  • {reason}")
                reasoning_lines.append(f"  Final Risk Score: 3.0 (Maximum)\n")
                _logger.info('Risk override applied for partner %s: %s',
                           partner.name, ', '.join(override_reason))

            # Determine risk level based on residual risk
            if residual_risk < 1.7:
                partner.risk_level = 'low'
                risk_band = "LOW (1.0 - 1.6)"
            elif residual_risk < 2.4:
                partner.risk_level = 'medium'
                risk_band = "MEDIUM (1.7 - 2.3)"
            else:
                partner.risk_level = 'high'
                risk_band = "HIGH (2.4 - 3.0)"

            reasoning_lines.append(f"Final Risk Assessment:")
            reasoning_lines.append(f"  Risk Score: {residual_risk:.2f}")
            reasoning_lines.append(f"  Risk Level: {risk_band}")
            reasoning_lines.append(f"  EDD Required: {'Yes' if partner.edd_required else 'No'}")

            partner.risk_reasoning = '\n'.join(reasoning_lines)

    @api.depends('pep_status', 'sanctions_status', 'is_company', 'child_ids.pep_status', 'child_ids.is_ubo', 'child_ids.sanctions_status')
    def _compute_customer_risk(self):
        """Calculate customer risk using weighted scoring like nex-systems."""
        for partner in self:
            # If confirmed sanctions match, return 3.0 immediately
            if partner.sanctions_status == 'match':
                latest_decision = self.env['aml.case.decision'].search([
                    ('case_id.partner_id', '=', partner.id),
                    ('case_id.case_type', 'in', ['sanctions', 'pep', 'adverse_media'])
                ], order='decided_date desc', limit=1)

                if latest_decision and latest_decision.outcome in ['true_positive', 'ongoing_monitoring', 'relationship_terminated']:
                    partner.customer_risk = 3.0
                    continue

            # Weighted scoring
            weighted_sum = 0.0
            total_weight = 0.0

            # Customer type (15%): individual = 1.0, company = 1.5
            customer_type_score = 1.0 if not partner.is_company else 1.5
            weighted_sum += customer_type_score * 0.15
            total_weight += 0.15

            # PEP exposure (30%): none = 1.0, domestic = 2.0, foreign = 3.0
            if partner.pep_status:
                pep_score = 3.0  # Assume foreign PEP for now
            elif partner.is_company and partner.child_ids.filtered(lambda c: c.pep_status and c.is_ubo):
                pep_score = 2.5  # UBO is PEP
            else:
                pep_score = 1.0
            weighted_sum += pep_score * 0.30
            total_weight += 0.30

            # Ownership structure (10%): transparent = 1.0, opaque = 2.5
            if partner.is_company:
                # Check if has many related parties (proxy for complex ownership)
                ownership_score = 2.5 if len(partner.child_ids) > 5 else 1.0
                weighted_sum += ownership_score * 0.10
                total_weight += 0.10

            # Country risk (15%) - will be same as geography_risk
            country_score = 1.0  # Default, will compute properly in geography
            weighted_sum += country_score * 0.15
            total_weight += 0.15

            # Residency (10%): local = 1.0, foreign = 2.0
            # For now, assume local if country matches organization country
            residency_score = 1.0
            weighted_sum += residency_score * 0.10
            total_weight += 0.10

            partner.customer_risk = round(weighted_sum / total_weight if total_weight > 0 else 2.0, 2)

    @api.depends('country_id', 'child_ids.country_id', 'child_ids.is_ubo')
    def _compute_geography_risk(self):
        """Calculate geography risk with decimal scoring."""
        # Country risk scores: 1.0 = low, 2.0 = medium, 3.0 = high
        HIGH_RISK_COUNTRIES = {'AF': 3.0, 'IR': 3.0, 'KP': 3.0, 'SY': 3.0, 'MM': 2.8, 'CU': 2.7, 'SD': 2.9, 'SO': 2.9}
        MEDIUM_RISK_COUNTRIES = {'PK': 2.3, 'IQ': 2.5, 'YE': 2.4, 'LY': 2.4, 'RU': 2.2, 'BY': 2.1}

        for partner in self:
            def get_country_score(country_code):
                if not country_code:
                    return 2.0
                if country_code in HIGH_RISK_COUNTRIES:
                    return HIGH_RISK_COUNTRIES[country_code]
                if country_code in MEDIUM_RISK_COUNTRIES:
                    return MEDIUM_RISK_COUNTRIES[country_code]
                return 1.0  # Low risk by default

            # Incorporation/residence country (50%)
            incorporation_score = get_country_score(partner.country_id.code if partner.country_id else None)

            # Nationality (30% for companies, 50% for individuals)
            nationality_score = incorporation_score  # Use same for now

            # UBO countries (20% for companies)
            ubo_score = 1.0
            if partner.is_company and partner.child_ids:
                ubos = partner.child_ids.filtered(lambda c: c.is_ubo)
                if ubos:
                    ubo_scores = [get_country_score(ubo.country_id.code if ubo.country_id else None) for ubo in ubos]
                    ubo_score = max(ubo_scores) if ubo_scores else 1.0

            # Weighted calculation
            if partner.is_company:
                geography_score = (incorporation_score * 0.5) + (nationality_score * 0.3) + (ubo_score * 0.2)
            else:
                geography_score = (incorporation_score * 0.5) + (nationality_score * 0.5)

            partner.geography_risk = round(geography_score, 2)

    @api.depends('product_ids', 'product_ids.risk_score')
    def _compute_product_risk(self):
        """Calculate product risk as highest risk from all products."""
        for partner in self:
            if partner.product_ids:
                # Get highest risk score (assuming products have risk_score field)
                risk_scores = partner.product_ids.mapped('risk_score')
                partner.product_risk = round(max(risk_scores), 2) if risk_scores else 2.0
            else:
                partner.product_risk = 2.0  # Default medium risk if no products

    def _compute_channel_risk(self):
        """Calculate channel risk with default scoring."""
        for partner in self:
            # Default to low risk - can be extended when onboarding channel data is added
            # In future: check partner.onboarding_channel_id.risk_score
            partner.channel_risk = 1.0

    @api.depends('customer_risk', 'geography_risk', 'product_risk', 'channel_risk')
    def _compute_risk_bars(self):
        """Generate HTML for single-color risk heatmap bars."""
        def get_bar_color(score):
            """Return color based on risk score."""
            if score < 1.7:
                return '#86efac'  # Green
            elif score < 2.4:
                return '#fde047'  # Yellow
            else:
                return '#ef4444'  # Red

        for partner in self:
            # Single bar for customer risk
            color = get_bar_color(partner.customer_risk or 1.0)
            partner.customer_risk_bar = f'<div style="width: 100%; height: 24px; border-radius: 6px; background-color: {color};"></div>'

            # Single bar for geography risk
            color = get_bar_color(partner.geography_risk or 1.0)
            partner.geography_risk_bar = f'<div style="width: 100%; height: 24px; border-radius: 6px; background-color: {color};"></div>'

            # Single bar for product risk
            color = get_bar_color(partner.product_risk or 2.0)
            partner.product_risk_bar = f'<div style="width: 100%; height: 24px; border-radius: 6px; background-color: {color};"></div>'

            # Single bar for channel risk
            color = get_bar_color(partner.channel_risk or 1.0)
            partner.channel_risk_bar = f'<div style="width: 100%; height: 24px; border-radius: 6px; background-color: {color};"></div>'

    @api.depends('risk_level')
    def _compute_edd_required(self):
        """Determine if Enhanced Due Diligence is required."""
        for partner in self:
            # EDD required for Medium and High risk customers
            partner.edd_required = partner.risk_level in ('medium', 'high')

    def action_assess_risk(self):
        """Manual risk assessment action."""
        self.ensure_one()
        self.last_assessment_date = fields.Date.today()
        # Set next review date based on risk level
        if self.risk_level == 'high':
            # High risk: review every 6 months
            self.next_review_date = fields.Date.add(fields.Date.today(), months=6)
        elif self.risk_level == 'medium':
            # Medium risk: review annually
            self.next_review_date = fields.Date.add(fields.Date.today(), months=12)
        else:
            # Low risk: review every 2 years
            self.next_review_date = fields.Date.add(fields.Date.today(), months=24)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Risk assessment completed. Risk Level: %s') % self.risk_level.upper(),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_screen_sanctions(self):
        """Perform sanctions screening via Yente API (multi-layer)."""
        self.ensure_one()

        # Get configuration
        ICP = self.env['ir.config_parameter'].sudo()
        yente_url = ICP.get_param('nexaml.yente_url', 'https://sanctions.nex.systems/match/default')
        api_key = ICP.get_param('nexaml.yente_api_key', '')
        threshold = float(ICP.get_param('nexaml.screening_threshold', '70.0'))
        screen_contacts = ICP.get_param('nexaml.screen_related_parties', 'True') == 'True'

        if not yente_url:
            raise UserError(_('Screening API URL not configured. Please configure in Settings > NexAML'))

        # Set status to pending
        self.sanctions_status = 'pending'
        self.last_screening_date = fields.Date.today()

        total_matches = 0
        screened_count = 1  # Primary customer

        # Layer 1: Screen primary customer
        try:
            result = self._perform_yente_screening(yente_url, api_key, threshold)
            total_matches += result['match_count']

            # Layer 2-4: Screen related parties (directors, shareholders, UBOs)
            if screen_contacts and not self.parent_id and self.child_ids:
                related_parties = self.child_ids.filtered(
                    lambda c: c.party_type in ('director', 'shareholder', 'ubo', 'signatory')
                )
                for contact in related_parties:
                    try:
                        contact.sanctions_status = 'pending'
                        contact_result = contact._perform_yente_screening(yente_url, api_key, threshold)
                        total_matches += contact_result['match_count']
                        screened_count += 1
                    except Exception as e:
                        _logger.warning('Failed to screen contact %s: %s', contact.name, str(e))
                        contact.sanctions_status = 'not_screened'

            if total_matches > 0:
                message = _('Multi-layer screening complete: %d match(es) found across %d parties') % (
                    total_matches, screened_count
                )
                msg_type = 'warning'
            else:
                message = _('Multi-layer screening complete: No matches found (%d parties screened)') % screened_count
                msg_type = 'success'

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': message,
                    'type': msg_type,
                    'sticky': True,
                }
            }
        except Exception as e:
            _logger.error('Sanctions screening failed for partner %s: %s', self.name, str(e))
            self.sanctions_status = 'not_screened'
            raise UserError(_('Screening failed: %s') % str(e))

    def _perform_yente_screening(self, yente_url, api_key='', threshold=70.0):
        """Perform actual Yente API call and process results."""
        self.ensure_one()

        # Determine schema based on partner type
        schema = 'Company' if self.is_company else 'Person'

        # Build entity properties
        properties = {
            'name': [self.name],
        }

        # Add optional fields based on schema
        if schema == 'Person':
            if self.country_id:
                properties['nationality'] = [self.country_id.code.lower()]
            if self.vat:
                properties['idNumber'] = [self.vat]
        else:  # Company
            if self.country_id:
                properties['jurisdiction'] = [self.country_id.code.lower()]
            if self.vat:
                properties['registrationNumber'] = [self.vat]

        # Prepare query-by-example payload (as per Yente API spec)
        payload = {
            'queries': {
                'entity1': {
                    'schema': schema,
                    'properties': properties
                }
            }
        }

        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'

        # Make API request
        _logger.info('Screening %s (%s) via Yente API: %s', self.name, schema, yente_url)

        try:
            response = requests.post(
                yente_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            _logger.error('Yente API request failed: %s', str(e))
            raise UserError(_('API connection failed: %s') % str(e))

        # Process results (Yente returns responses keyed by query ID)
        responses = data.get('responses', {})
        entity1_response = responses.get('entity1', {})
        results = entity1_response.get('results', [])

        match_count = 0
        highest_score = 0.0
        threshold_decimal = threshold / 100.0  # Yente uses 0.0-1.0 scores

        for result in results:
            score = result.get('score', 0.0)
            if score >= threshold_decimal:
                match_count += 1
                highest_score = max(highest_score, score * 100)  # Convert to percentage for display

                # Create screening record and case
                self._create_screening_record(result, score * 100)

                # Check for PEP status in matched entity
                entity = result.get('entity', {})
                topics = entity.get('topics', [])
                if 'role.pep' in topics:
                    self.pep_status = True
                    _logger.info('PEP status detected for partner %s', self.name)

        # Update partner status
        if match_count > 0:
            self.sanctions_status = 'match'
            status = 'match'
        else:
            self.sanctions_status = 'clear'
            status = 'clear'

        return {
            'status': status,
            'match_count': match_count,
            'highest_score': highest_score,
        }

    def _create_screening_record(self, result, score):
        """Create aml.screening record and case from Yente result."""
        self.ensure_one()

        entity = result.get('entity', {})
        properties = entity.get('properties', {})

        # Extract matched information
        matched_name = ', '.join(properties.get('name', [self.name])[:1])
        matched_countries = ', '.join(properties.get('country', [])[:3])
        datasets = ', '.join(entity.get('datasets', [])[:3])
        topics = entity.get('topics', [])

        screening_vals = {
            'partner_id': self.id,
            'screening_type': 'sanctions',
            'status': 'match',
            'match_score': score,
            'matched_name': matched_name,
            'matched_entity_id': entity.get('id'),
            'matched_countries': matched_countries,
            'matched_datasets': datasets,
            'screening_data': json.dumps(result, indent=2),
        }

        screening = self.env['aml.screening'].sudo().create(screening_vals)
        _logger.info('Created screening record %s for partner %s (score: %.2f)',
                     screening.name, self.name, score)

        # Post message to partner (case will be auto-created by screening model)
        self.message_post(
            body=_('Sanctions match detected (score: %.2f%%). Case created for investigation.') % score,
            subject=_('Sanctions Match'),
            message_type='notification',
        )

        return screening

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to auto-screen if enabled."""
        partners = super(ResPartner, self).create(vals_list)

        # Check if auto-screening is enabled
        ICP = self.env['ir.config_parameter'].sudo()
        auto_screen = ICP.get_param('nexaml.auto_screen_on_create', 'False')

        if auto_screen == 'True':
            for partner in partners:
                if not partner.parent_id:
                    # Only screen main contacts, not child contacts
                    try:
                        partner.action_screen_sanctions()
                    except Exception as e:
                        _logger.warning('Auto-screening failed for new partner %s: %s',
                                       partner.name, str(e))

        return partners

    @api.model
    def cron_rescreen_partners(self):
        """Periodic rescreening of high-risk partners and previous matches."""
        _logger.info('Starting periodic AML rescreening...')

        # Find partners that need rescreening:
        # 1. High-risk partners
        # 2. Partners with previous sanctions matches
        # 3. Partners not screened in last 30 days
        domain = [
            '|', '|',
            ('risk_level', '=', 'high'),
            ('sanctions_status', '=', 'match'),
            '&',
            ('last_screening_date', '!=', False),
            ('last_screening_date', '<', fields.Date.subtract(fields.Date.today(), days=30))
        ]

        partners = self.search(domain, limit=100)
        _logger.info('Found %d partners for rescreening', len(partners))

        screened_count = 0
        failed_count = 0

        for partner in partners:
            try:
                partner.action_screen_sanctions()
                screened_count += 1
            except Exception as e:
                _logger.error('Rescreening failed for partner %s: %s', partner.name, str(e))
                failed_count += 1

        _logger.info('Periodic rescreening completed: %d screened, %d failed',
                     screened_count, failed_count)

        return True

    @api.model
    def cron_reassess_risk(self):
        """Periodic risk reassessment based on review dates and triggers."""
        _logger.info('Starting periodic risk reassessment...')

        today = fields.Date.today()

        # Find partners that need reassessment:
        # 1. Next review date is today or past
        # 2. High-risk partners not assessed in last 180 days (6 months)
        # 3. Medium-risk partners not assessed in last 365 days (12 months)
        # 4. Low-risk partners not assessed in last 730 days (24 months)
        domain = [
            '|', '|', '|',
            ('next_review_date', '<=', today),
            '&', ('risk_level', '=', 'high'),
                 ('last_assessment_date', '<', fields.Date.subtract(today, days=180)),
            '&', ('risk_level', '=', 'medium'),
                 ('last_assessment_date', '<', fields.Date.subtract(today, days=365)),
            '&', ('risk_level', '=', 'low'),
                 ('last_assessment_date', '<', fields.Date.subtract(today, days=730))
        ]

        partners = self.search(domain, limit=100)
        _logger.info('Found %d partners for risk reassessment', len(partners))

        reassessed_count = 0

        for partner in partners:
            try:
                partner.action_assess_risk()
                reassessed_count += 1
            except Exception as e:
                _logger.error('Risk reassessment failed for partner %s: %s', partner.name, str(e))

        _logger.info('Periodic risk reassessment completed: %d partners reassessed', reassessed_count)

        return True
