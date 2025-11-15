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

    # Risk Factor Fields
    customer_risk = fields.Selection(
        [('1', 'Low'), ('2', 'Medium'), ('3', 'High')],
        string='Customer Risk Factor',
        default='1',
        help='Customer-specific risk factors (occupation, business type, etc.)'
    )
    geography_risk = fields.Selection(
        [('1', 'Low'), ('2', 'Medium'), ('3', 'High')],
        string='Geography Risk Factor',
        default='1',
        help='Geographic risk based on country/jurisdiction'
    )
    product_risk = fields.Selection(
        [('1', 'Low'), ('2', 'Medium'), ('3', 'High')],
        string='Product Risk Factor',
        compute='_compute_product_risk',
        store=True,
        help='Highest risk level from associated products'
    )
    channel_risk = fields.Selection(
        [('1', 'Low'), ('2', 'Medium'), ('3', 'High')],
        string='Channel Risk Factor',
        default='1',
        help='Delivery channel risk (online, face-to-face, etc.)'
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

            # Component breakdown
            reasoning_lines.append("Risk Components:")
            reasoning_lines.append(f"  • Customer Risk: {customer_risk} ({dict(partner._fields['customer_risk'].selection).get(str(int(customer_risk)))})")
            reasoning_lines.append(f"  • Geography Risk: {geography_risk} ({dict(partner._fields['geography_risk'].selection).get(str(int(geography_risk)))})")
            reasoning_lines.append(f"  • Product Risk: {product_risk} ({dict(partner._fields['product_risk'].selection).get(str(int(product_risk)))})")
            reasoning_lines.append(f"  • Channel Risk: {channel_risk} ({dict(partner._fields['channel_risk'].selection).get(str(int(channel_risk)))})\n")

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

            # Scenario-Based Risk Overrides
            override_high = False
            override_reason = []

            # Override 1: PEP Status (customer or related parties)
            if partner.pep_status:
                override_high = True
                override_reason.append('Customer is PEP')

            # Check UBOs and related parties for PEP status
            if partner.child_ids:
                pep_contacts = partner.child_ids.filtered(lambda c: c.pep_status and c.is_ubo)
                if pep_contacts:
                    override_high = True
                    override_reason.append('UBO is PEP')

            # Override 2: Sanctions Match or Open Case (customer or UBOs)
            if partner.sanctions_status == 'match':
                # Check if there are open screening cases
                open_cases = self.env['aml.case'].search([
                    ('partner_id', '=', partner.id),
                    ('case_type', '=', 'screening'),
                    ('state', 'in', ['open', 'investigating', 'under_review', 'pending_info'])
                ])
                if open_cases:
                    override_high = True
                    override_reason.append(f'Potential sanctions match ({len(open_cases)} open case(s))')
                else:
                    # Resolved cases - check decision
                    resolved_cases = self.env['aml.case'].search([
                        ('partner_id', '=', partner.id),
                        ('case_type', '=', 'screening'),
                        ('state', 'in', ['resolved_approved', 'resolved_rejected', 'closed'])
                    ], order='closed_date desc', limit=1)
                    if resolved_cases:
                        case = resolved_cases[0]
                        # If decision is not false positive, it's a confirmed match
                        # Check latest decision outcome
                        if case.decision_ids:
                            latest_decision = case.decision_ids.sorted('decided_date', reverse=True)[0]
                            if latest_decision.outcome != 'false_positive':
                                override_high = True
                                override_reason.append('Confirmed sanctions match')
                        else:
                            # No decisions recorded - assume confirmed match
                            override_high = True
                            override_reason.append('Confirmed sanctions match')

            if partner.child_ids:
                sanctioned_contacts = partner.child_ids.filtered(
                    lambda c: c.sanctions_status == 'match' and c.is_ubo
                )
                if sanctioned_contacts:
                    override_high = True
                    override_reason.append('UBO sanctions match')

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

    @api.depends('product_ids', 'product_ids.risk_score')
    def _compute_product_risk(self):
        """Calculate product risk as highest risk from all products."""
        for partner in self:
            if partner.product_ids:
                # Get highest risk score
                risk_scores = partner.product_ids.mapped('risk_score')
                partner.product_risk = max(risk_scores) if risk_scores else '1'
            else:
                partner.product_risk = '1'

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

        screening = self.env['aml.screening'].create(screening_vals)
        _logger.info('Created screening record %s for partner %s (score: %.2f)',
                     screening.name, self.name, score)

        # Create case for sanctions match
        case_description = f"""
Sanctions screening match detected:

Match Score: {score:.2f}%
Matched Name: {matched_name}
Matched Entity ID: {entity.get('id')}
Datasets: {datasets}
Countries: {matched_countries}
Topics: {', '.join(topics)}

Customer: {self.name}
Customer Type: {'Company' if self.is_company else 'Person'}
Country: {self.country_id.name if self.country_id else 'N/A'}
        """

        # Determine priority based on score and topics
        priority = 'critical' if score >= 90 or 'sanction' in topics else 'high'

        case_vals = {
            'partner_id': self.id,
            'case_type': 'screening',
            'state': 'open',
            'priority': priority,
            'description': case_description.strip(),
            'assigned_to': self.env.user.id,
        }

        case = self.env['aml.case'].create(case_vals)
        _logger.info('Created case %s for sanctions match on partner %s', case.name, self.name)

        # Post message to partner
        self.message_post(
            body=_('Sanctions match detected (score: %.2f%%). Case %s created for investigation.') % (score, case.name),
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
