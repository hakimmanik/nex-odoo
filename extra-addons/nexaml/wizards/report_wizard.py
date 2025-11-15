# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import base64
import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ReportWizard(models.TransientModel):
    """Wizard to generate compliance reports."""
    _name = 'report.wizard'
    _description = 'Report Wizard'

    report_type = fields.Selection(
        [('sar', 'Suspicious Activity Report (SAR)'),
         ('str', 'Suspicious Transaction Report (STR)'),
         ('dpmsr', 'Domestic PEP Monitoring & Sanctions Report (DPMSR)'),
         ('pnmr', 'PEP Name Match Report (PNMR)'),
         ('cnmr', 'Country Name Match Report (CNMR)'),
         ('aif', 'Account Information Form (AIF)'),
         ('aift', 'Account Information Form - Threshold (AIFT)'),
         ('ecdd', 'Enhanced Customer Due Diligence (ECDD)'),
         ('basic', 'Basic Customer Report'),
         ('periodic', 'Periodic Compliance Summary'),
         ('risk', 'Customer Risk Summary')],
        string='Report Type',
        required=True,
        default='periodic',
        help='Type of report to generate'
    )
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=fields.Date.today,
        help='Start date for report period'
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=fields.Date.today,
        help='End date for report period'
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Customers',
        help='Select specific customers (optional)'
    )
    case_ids = fields.Many2many(
        'aml.case',
        string='Cases',
        help='Select specific cases for SAR/STR reports'
    )
    # Output format is auto-determined by report type (matching nex-systems)
    # BASIC = xlsx, all others = xml (goAML)
    output_format = fields.Selection(
        [('xlsx', 'Excel'),
         ('xml', 'XML (goAML)')],
        string='Output Format',
        compute='_compute_output_format',
        store=True,
        readonly=True,
        help='Output format (auto-determined by report type)'
    )
    include_narrative = fields.Boolean(
        string='Include Narrative',
        default=True,
        help='Include narrative section in SAR/STR reports'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        help='Company for report'
    )

    # Advanced Filtering Fields - All Optional
    query_type = fields.Selection(
        [('single', 'Single Customer'),
         ('advanced', 'Advanced Filtering')],
        string='Query Type',
        default='single',
        help='Select single customer or use advanced filters'
    )

    # Customer Filters (Optional)
    filter_customer_type = fields.Selection(
        [('person', 'Individual'),
         ('company', 'Company')],
        string='Customer Type',
        help='Filter by customer type (optional)'
    )
    filter_customer_status = fields.Selection(
        [('active', 'Active'),
         ('archived', 'Archived')],
        string='Customer Status',
        help='Filter by customer status (optional)'
    )
    filter_risk_level = fields.Selection(
        [('low', 'Low'),
         ('medium', 'Medium'),
         ('high', 'High')],
        string='Risk Level',
        help='Filter by risk level (optional)'
    )
    filter_pep_status = fields.Selection(
        [('yes', 'PEP Only'),
         ('no', 'Non-PEP Only')],
        string='PEP Status',
        help='Filter by PEP status (optional)'
    )
    filter_country_ids = fields.Many2many(
        'res.country',
        'report_wizard_country_rel',
        'wizard_id',
        'country_id',
        string='Countries',
        help='Filter by specific countries (optional)'
    )
    filter_nationality_code = fields.Many2one(
        'res.country',
        string='Nationality',
        help='Filter by nationality (optional)'
    )
    filter_country_of_birth = fields.Many2one(
        'res.country',
        string='Country of Birth',
        help='Filter by country of birth (optional)'
    )
    filter_resid_country_code = fields.Many2one(
        'res.country',
        string='Residence Country',
        help='Filter by residence country (optional)'
    )
    filter_edd_required = fields.Boolean(
        string='EDD Required Only',
        help='Show only customers requiring Enhanced Due Diligence (optional)'
    )
    filter_sanctions_status = fields.Selection(
        [('match', 'Sanctions Match'),
         ('clear', 'Clear'),
         ('pending', 'Pending')],
        string='Sanctions Status',
        help='Filter by sanctions screening status (optional)'
    )
    filter_customer_name = fields.Char(
        string='Customer Name',
        help='Search by customer name (optional)'
    )

    # Transaction Filters (Optional)
    filter_amount_min = fields.Float(
        string='Min Amount',
        help='Minimum transaction amount (optional)'
    )
    filter_amount_max = fields.Float(
        string='Max Amount',
        help='Maximum transaction amount (optional)'
    )
    filter_currency_ids = fields.Many2many(
        'res.currency',
        'report_wizard_currency_rel',
        'wizard_id',
        'currency_id',
        string='Currencies',
        help='Filter by specific currencies (optional)'
    )
    # Transaction type filtering removed - account.move.type not available in Odoo 19
    # Use move_type field directly on account.move if needed
    # filter_transaction_types = fields.Many2many(
    #     'account.move.type',
    #     string='Transaction Types',
    #     help='Filter by transaction types (optional)'
    # )
    filter_payment_methods = fields.Selection([
        ('cash', 'Cash'),
        ('crypto', 'Cryptocurrency'),
        ('international_wire', 'International Wire'),
        ('domestic_wire', 'Domestic Wire'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_payment', 'Mobile Payment')
    ], string='Payment Method', help='Filter by payment method (optional)')
    filter_channel = fields.Selection([
        ('branch', 'Branch'),
        ('atm', 'ATM'),
        ('online', 'Online'),
        ('mobile', 'Mobile'),
        ('phone', 'Phone'),
        ('agent', 'Agent')
    ], string='Channel', help='Filter by transaction channel (optional)')

    # KYC/Risk Filters (Optional)
    filter_risk_score_min = fields.Float(
        string='Min Risk Score',
        help='Minimum risk score (optional)'
    )
    filter_risk_score_max = fields.Float(
        string='Max Risk Score',
        help='Maximum risk score (optional)'
    )
    filter_onboarding_date_from = fields.Date(
        string='Onboarding From',
        help='Filter customers onboarded from this date (optional)'
    )
    filter_onboarding_date_to = fields.Date(
        string='Onboarding To',
        help='Filter customers onboarded until this date (optional)'
    )

    # Geographic/Corridor Filters (Optional)
    filter_domestic_only = fields.Boolean(
        string='Domestic Only',
        help='Show only domestic transactions (optional)'
    )
    filter_cross_border_only = fields.Boolean(
        string='Cross-Border Only',
        help='Show only cross-border transactions (optional)'
    )

    # Additional Filters (Optional)
    filter_source_of_funds = fields.Char(
        string='Source of Funds',
        help='Filter by source of funds (optional)'
    )
    filter_occupation = fields.Char(
        string='Occupation',
        help='Filter by occupation (optional)'
    )
    filter_employer = fields.Char(
        string='Employer',
        help='Filter by employer (optional)'
    )
    filter_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender', help='Filter by gender (optional)')
    filter_entity_type = fields.Char(
        string='Entity Type',
        help='Filter by entity type for companies (optional)'
    )
    filter_sector = fields.Char(
        string='Sector',
        help='Filter by business sector (optional)'
    )
    filter_has_expired_docs = fields.Boolean(
        string='Expired Documents Only',
        help='Show only customers with expired documents (optional)'
    )

    threshold_amount = fields.Float(
        string='Threshold Amount',
        default=10000,
        help='Threshold amount for AIFT reports'
    )

    @api.depends('report_type')
    def _compute_output_format(self):
        """Auto-determine output format based on report type (matching nex-systems)."""
        for record in self:
            if record.report_type == 'basic':
                record.output_format = 'xlsx'
            else:
                # All regulatory reports (STR, SAR, DPMSR, PNMR, CNMR, AIF, AIFT, ECDD) = XML
                record.output_format = 'xml'

    @api.onchange('report_type')
    def _onchange_report_type(self):
        """Update fields based on report type."""
        # Output format is auto-computed
        pass

    def _build_advanced_filter_domain(self):
        """Build comprehensive domain for advanced filtering - all filters optional."""
        domain = []

        # Date range (always include if provided)
        if self.date_from:
            domain.append(('create_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('create_date', '<=', self.date_to))

        # Customer Filters (all optional)
        if self.filter_customer_type:
            if self.filter_customer_type == 'company':
                domain.append(('is_company', '=', True))
            else:
                domain.append(('is_company', '=', False))

        if self.filter_customer_status:
            domain.append(('active', '=', self.filter_customer_status == 'active'))

        if self.filter_risk_level:
            domain.append(('risk_level', '=', self.filter_risk_level))

        if self.filter_pep_status:
            domain.append(('pep_status', '=', self.filter_pep_status == 'yes'))

        if self.filter_country_ids:
            domain.append(('country_id', 'in', self.filter_country_ids.ids))

        if self.filter_nationality_code:
            domain.append(('country_id', '=', self.filter_nationality_code.id))

        if self.filter_resid_country_code:
            domain.append(('country_id', '=', self.filter_resid_country_code.id))

        if self.filter_edd_required:
            domain.append(('edd_required', '=', True))

        if self.filter_sanctions_status:
            domain.append(('sanctions_status', '=', self.filter_sanctions_status))

        if self.filter_customer_name:
            domain.append(('name', 'ilike', self.filter_customer_name))

        # KYC/Risk Score Filters (optional)
        if self.filter_risk_score_min:
            domain.append(('risk_score', '>=', self.filter_risk_score_min))

        if self.filter_risk_score_max:
            domain.append(('risk_score', '<=', self.filter_risk_score_max))

        if self.filter_onboarding_date_from:
            domain.append(('create_date', '>=', self.filter_onboarding_date_from))

        if self.filter_onboarding_date_to:
            domain.append(('create_date', '<=', self.filter_onboarding_date_to))

        # Additional Optional Filters
        if self.filter_source_of_funds:
            domain.append(('source_of_funds', 'ilike', self.filter_source_of_funds))

        if self.filter_occupation:
            domain.append(('occupation', 'ilike', self.filter_occupation))

        if self.filter_employer:
            domain.append(('employer', 'ilike', self.filter_employer))

        return domain

    def _build_transaction_filter_domain(self):
        """Build domain for transaction filtering - all filters optional."""
        domain = []

        # Date range
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))

        # Amount filters (optional)
        if self.filter_amount_min:
            domain.append(('amount_total', '>=', self.filter_amount_min))

        if self.filter_amount_max:
            domain.append(('amount_total', '<=', self.filter_amount_max))

        # Currency filter (optional)
        if self.filter_currency_ids:
            domain.append(('currency_id', 'in', self.filter_currency_ids.ids))

        # Payment method filter (optional)
        if self.filter_payment_methods:
            domain.append(('payment_method', '=', self.filter_payment_methods))

        # Domestic/Cross-border filters (optional)
        if self.filter_domestic_only:
            domain.append(('partner_id.country_id', '=', self.company_id.country_id.id))

        if self.filter_cross_border_only:
            domain.append(('partner_id.country_id', '!=', self.company_id.country_id.id))

        return domain

    def action_generate_report(self):
        """Generate the selected report."""
        self.ensure_one()

        # Validate inputs
        if self.date_from > self.date_to:
            raise UserError(_('From Date cannot be after To Date'))

        if self.report_type == 'sar':
            return self._generate_sar()
        elif self.report_type == 'str':
            return self._generate_str()
        elif self.report_type == 'dpmsr':
            return self._generate_dpmsr()
        elif self.report_type == 'pnmr':
            return self._generate_pnmr()
        elif self.report_type == 'cnmr':
            return self._generate_cnmr()
        elif self.report_type == 'aif':
            return self._generate_aif()
        elif self.report_type == 'aift':
            return self._generate_aift()
        elif self.report_type == 'ecdd':
            return self._generate_ecdd()
        elif self.report_type == 'basic':
            return self._generate_basic()
        elif self.report_type == 'periodic':
            return self._generate_periodic_summary()
        elif self.report_type == 'risk':
            return self._generate_risk_summary()

        raise UserError(_('Unknown report type'))

    def _generate_sar(self):
        """Generate Suspicious Activity Report."""
        # Case selection is NEVER required - auto-discover using filters
        cases = self.case_ids

        if not cases:
            if self.query_type == 'advanced':
                # Use advanced filters to find cases
                partner_domain = self._build_advanced_filter_domain()
                partners = self.env['res.partner'].search(partner_domain)
                if partners:
                    case_domain = [
                        ('partner_id', 'in', partners.ids),
                        ('opened_date', '>=', self.date_from),
                        ('opened_date', '<=', self.date_to)
                    ]
                    cases = self.env['aml.case'].search(case_domain)
            elif self.partner_ids:
                # Use selected partners to find cases
                case_domain = [
                    ('partner_id', 'in', self.partner_ids.ids),
                    ('opened_date', '>=', self.date_from),
                    ('opened_date', '<=', self.date_to)
                ]
                cases = self.env['aml.case'].search(case_domain)

            # Fallback: get all cases in date range
            if not cases:
                case_domain = [
                    ('opened_date', '>=', self.date_from),
                    ('opened_date', '<=', self.date_to)
                ]
                cases = self.env['aml.case'].search(case_domain)

        if not cases:
            raise UserError(_('No cases found for the specified date range and filters. Please adjust your criteria or create cases first.'))

        # Store found cases
        self.case_ids = cases

        # SAR always outputs XML (goAML format) - matching nex-systems
        return self._export_goaml_sar()

    def _generate_str(self):
        """Generate Suspicious Transaction Report."""
        # Case selection is NEVER required - auto-discover using filters
        cases = self.case_ids

        if not cases:
            if self.query_type == 'advanced':
                # Use advanced filters to find cases
                partner_domain = self._build_advanced_filter_domain()
                partners = self.env['res.partner'].search(partner_domain)
                if partners:
                    case_domain = [
                        ('partner_id', 'in', partners.ids),
                        ('opened_date', '>=', self.date_from),
                        ('opened_date', '<=', self.date_to)
                    ]
                    cases = self.env['aml.case'].search(case_domain)
            elif self.partner_ids:
                # Use selected partners to find cases
                case_domain = [
                    ('partner_id', 'in', self.partner_ids.ids),
                    ('opened_date', '>=', self.date_from),
                    ('opened_date', '<=', self.date_to)
                ]
                cases = self.env['aml.case'].search(case_domain)

            # Fallback: get all cases in date range
            if not cases:
                case_domain = [
                    ('opened_date', '>=', self.date_from),
                    ('opened_date', '<=', self.date_to)
                ]
                cases = self.env['aml.case'].search(case_domain)

        if not cases:
            raise UserError(_('No cases found for the specified date range and filters. Please adjust your criteria or create cases first.'))

        # Store found cases
        self.case_ids = cases

        # STR always outputs XML (goAML format) - matching nex-systems
        return self._export_goaml_str()

    def _generate_periodic_summary(self):
        """Generate Periodic Compliance Summary - XLSX output."""
        return self._export_excel_periodic()

    def _generate_risk_summary(self):
        """Generate Customer Risk Summary - XLSX output."""
        return self._export_excel_risk()

    def _generate_dpmsr(self):
        """Generate Domestic PEP Monitoring & Sanctions Report."""
        # Use advanced filtering if selected
        if self.query_type == 'advanced':
            domain = self._build_advanced_filter_domain()
            # Additional DPMSR-specific filters
            domain.append('|')
            domain.append(('pep_status', '=', True))
            domain.append(('sanctions_status', '=', 'match'))
            partners = self.env['res.partner'].search(domain)
        elif self.partner_ids:
            partners = self.partner_ids
        else:
            # Default: PEP and sanctioned entities in date range
            domain = [
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to),
                '|',
                ('pep_status', '=', True),
                ('sanctions_status', '=', 'match')
            ]
            partners = self.env['res.partner'].search(domain)

        # DPMSR outputs XML (goAML format) - matching nex-systems
        return self._export_goaml_dpmsr(partners)

    def _generate_pnmr(self):
        """Generate PEP Name Match Report."""
        # Filter for PEP matches
        domain = [
            ('pep_status', '=', True),
            ('create_date', '>=', self.date_from),
            ('create_date', '<=', self.date_to)
        ]
        if self.partner_ids:
            domain.append(('id', 'in', self.partner_ids.ids))

        partners = self.env['res.partner'].search(domain)

        # PNMR outputs XML (goAML format) - matching nex-systems
        return self._export_goaml_pnmr(partners)

    def _generate_cnmr(self):
        """Generate Country Name Match Report."""
        # Filter for high-risk countries
        high_risk_countries = ['IR', 'KP', 'SY']  # Iran, North Korea, Syria
        domain = [
            ('country_id.code', 'in', high_risk_countries),
            ('create_date', '>=', self.date_from),
            ('create_date', '<=', self.date_to)
        ]
        if self.partner_ids:
            domain.append(('id', 'in', self.partner_ids.ids))

        partners = self.env['res.partner'].search(domain)

        # CNMR outputs XML (goAML format) - matching nex-systems
        return self._export_goaml_cnmr(partners)

    def _generate_aif(self):
        """Generate Account Information Form."""
        # Comprehensive customer account information
        if not self.partner_ids:
            raise UserError(_('Please select at least one customer for AIF report'))

        # AIF outputs XML (goAML format) - matching nex-systems
        return self._export_goaml_aif(self.partner_ids)

    def _generate_aift(self):
        """Generate Account Information Form - Threshold."""
        # Filter customers with transactions above threshold
        threshold = self.threshold_amount or 10000

        # AIFT outputs XML (goAML format) - matching nex-systems
        return self._export_goaml_aift(self.partner_ids, threshold)

    def _generate_ecdd(self):
        """Generate Enhanced Customer Due Diligence Report."""
        # Filter for high-risk customers requiring EDD
        domain = [
            ('edd_required', '=', True),
            ('create_date', '>=', self.date_from),
            ('create_date', '<=', self.date_to)
        ]
        if self.partner_ids:
            domain.append(('id', 'in', self.partner_ids.ids))

        partners = self.env['res.partner'].search(domain)

        # ECDD outputs XML (goAML format) - matching nex-systems
        return self._export_goaml_ecdd(partners)

    def _generate_basic(self):
        """Generate Basic Customer Report - XLSX output only."""
        # BASIC always outputs XLSX - matching nex-systems
        return self._export_excel_basic()

    # Risk Indicator Derivation & Scoring Methods
    def _derive_risk_indicators(self, case):
        """
        Derive risk indicators from case data and transactions.
        Based on nex-systems implementation.
        """
        indicators = set()

        # Get transactions from case
        transactions = case.transaction_ids if hasattr(case, 'transaction_ids') else []

        # Transaction-based indicators
        for tx in transactions:
            # Large amount indicator (>= 10,000)
            if tx.amount >= 10000:
                indicators.add('large_amount')

            # Third party indicators
            if hasattr(tx, 'direction'):
                if tx.direction == 'in' and tx.counterparty_id:
                    indicators.add('third_party_funding')
                elif tx.direction == 'out' and tx.counterparty_id:
                    indicators.add('third_party_payments')

        # Analyze case description for patterns
        description = (case.description or '').lower()

        # Structuring indicator
        if 'structur' in description or 'smurfing' in description:
            indicators.add('structuring')

        # Terrorism financing indicator
        if any(keyword in description for keyword in ['terror', 'ml', 'money launder', 'financing']):
            indicators.add('terrorism_finance')

        # Unusual patterns
        if 'unusual' in description or 'suspicious' in description:
            indicators.add('unusual_pattern')

        # Check case type for additional indicators
        if case.case_type in ('sanctions', 'pep'):
            indicators.add('sanctions_pep_match')

        return list(indicators)

    def _calculate_risk_score(self, indicators):
        """
        Calculate risk score based on weighted indicators.
        Returns dict with score (1.0-3.0) and risk_level (low/medium/high).
        """
        # Indicator weights (based on nex-systems)
        weights = {
            'terrorism_finance': 3.0,
            'structuring': 2.5,
            'large_amount': 1.5,
            'third_party_funding': 2.0,
            'third_party_payments': 2.0,
            'unusual_pattern': 1.8,
            'sanctions_pep_match': 2.8,
        }

        if not indicators:
            return {'score': 1.0, 'risk_level': 'low'}

        # Calculate weighted average
        total_weight = 0.0
        count = 0

        for indicator in indicators:
            weight = weights.get(indicator, 1.0)
            total_weight += weight
            count += 1

        avg_score = total_weight / count if count > 0 else 1.0

        # Determine risk level
        if avg_score >= 2.5:
            risk_level = 'high'
            normalized_score = 3.0
        elif avg_score >= 1.5:
            risk_level = 'medium'
            normalized_score = 2.0
        else:
            risk_level = 'low'
            normalized_score = 1.0

        return {
            'score': normalized_score,
            'risk_level': risk_level,
            'avg_score': round(avg_score, 2)
        }

    # XML Export Methods for Regulatory Reports (goAML format)
    def _export_goaml_dpmsr(self, partners):
        """Export DPMSR (Domestic PEP Monitoring & Sanctions Report) as goAML XML."""
        xml_content = self._generate_goaml_xml('DPMSR', partners=partners)
        return self._download_goaml_file(xml_content, 'dpmsr')

    def _export_goaml_pnmr(self, partners):
        """Export PNMR (PEP Name Match Report) as goAML XML."""
        xml_content = self._generate_goaml_xml('PNMR', partners=partners)
        return self._download_goaml_file(xml_content, 'pnmr')

    def _export_goaml_cnmr(self, partners):
        """Export CNMR (Country Name Match Report) as goAML XML."""
        xml_content = self._generate_goaml_xml('CNMR', partners=partners)
        return self._download_goaml_file(xml_content, 'cnmr')

    def _export_goaml_aif(self, partners):
        """Export AIF (Account Information Form) as goAML XML."""
        xml_content = self._generate_goaml_xml('AIF', partners=partners)
        return self._download_goaml_file(xml_content, 'aif')

    def _export_goaml_aift(self, partners, threshold):
        """Export AIFT (Account Information Form - Threshold) as goAML XML."""
        xml_content = self._generate_goaml_xml('AIFT', partners=partners, threshold=threshold)
        return self._download_goaml_file(xml_content, 'aift')

    def _export_goaml_ecdd(self, partners):
        """Export ECDD (Enhanced Customer Due Diligence) as goAML XML."""
        xml_content = self._generate_goaml_xml('ECDD', partners=partners)
        return self._download_goaml_file(xml_content, 'ecdd')

    # Excel Export Methods (BASIC report and summaries only)

    def _export_excel_periodic(self):
        """Export Periodic Summary as Excel."""
        try:
            import xlsxwriter
            from io import BytesIO
        except ImportError:
            raise UserError(_('xlsxwriter library not installed'))

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Periodic Compliance Summary')

        header_format = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1})

        headers = [
            'Period', 'Total Customers', 'New Customers', 'High Risk Customers',
            'Total Transactions', 'Total Amount', 'Currency', 'Open Cases',
            'Closed Cases', 'PEP Customers', 'Sanctioned Customers', 'EDD Required'
        ]
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        total_customers = self.env['res.partner'].search_count([
            ('create_date', '<=', self.date_to)
        ])
        new_customers = self.env['res.partner'].search_count([
            ('create_date', '>=', self.date_from),
            ('create_date', '<=', self.date_to)
        ])
        high_risk = self.env['res.partner'].search_count([
            ('risk_level', '=', 'high')
        ])
        total_txs = self.env['account.move'].search_count([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', '=', 'posted')
        ])
        total_amount = sum(self.env['account.move'].search([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', '=', 'posted')
        ]).mapped('amount_total'))
        open_cases = self.env['aml.case'].search_count([
            ('opened_date', '>=', self.date_from),
            ('opened_date', '<=', self.date_to),
            ('state', 'in', ['open', 'investigating'])
        ])
        closed_cases = self.env['aml.case'].search_count([
            ('opened_date', '>=', self.date_from),
            ('closed_date', '<=', self.date_to),
            ('state', 'in', ['closed', 'resolved_approved', 'resolved_rejected'])
        ])
        pep_customers = self.env['res.partner'].search_count([('pep_status', '=', True)])
        sanctioned = self.env['res.partner'].search_count([('sanctions_status', '=', 'match')])
        edd_required = self.env['res.partner'].search_count([('edd_required', '=', True)])

        period = f"{self.date_from.strftime('%Y-%m-%d')} to {self.date_to.strftime('%Y-%m-%d')}"

        worksheet.write(1, 0, period)
        worksheet.write(1, 1, total_customers)
        worksheet.write(1, 2, new_customers)
        worksheet.write(1, 3, high_risk)
        worksheet.write(1, 4, total_txs)
        worksheet.write(1, 5, total_amount)
        worksheet.write(1, 6, self.company_id.currency_id.name or 'AED')
        worksheet.write(1, 7, open_cases)
        worksheet.write(1, 8, closed_cases)
        worksheet.write(1, 9, pep_customers)
        worksheet.write(1, 10, sanctioned)
        worksheet.write(1, 11, edd_required)

        for i in range(len(headers)):
            worksheet.set_column(i, i, 18)

        workbook.close()
        output.seek(0)
        xlsx_data = output.read()
        output.close()

        filename = f'periodic_compliance_summary_{fields.Date.today()}.xlsx'
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(xlsx_data),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def _export_excel_risk(self):
        """Export Risk Summary as Excel."""
        try:
            import xlsxwriter
            from io import BytesIO
        except ImportError:
            raise UserError(_('xlsxwriter library not installed. Please install it with: pip install xlsxwriter'))

        # Create Excel file
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Customer Risk Summary')

        # Formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9E1F2',
            'border': 1
        })
        high_risk_format = workbook.add_format({
            'bg_color': '#FFC7CE',
            'font_color': '#9C0006'
        })
        medium_risk_format = workbook.add_format({
            'bg_color': '#FFEB9C',
            'font_color': '#9C6500'
        })
        low_risk_format = workbook.add_format({
            'bg_color': '#C6EFCE',
            'font_color': '#006100'
        })

        # Headers
        headers = ['Customer', 'Risk Level', 'Inherent Risk', 'Residual Risk',
                   'EDD Required', 'Last Assessment', 'Next Review', 'Sanctions Status']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # Get partners
        if self.partner_ids:
            partners = self.partner_ids
        else:
            partners = self.env['res.partner'].search([
                ('is_company', '=', True),
                ('customer_rank', '>', 0)
            ])

        # Write data
        row = 1
        for partner in partners:
            # Risk format based on level
            if partner.risk_level == 'high':
                risk_format = high_risk_format
            elif partner.risk_level == 'medium':
                risk_format = medium_risk_format
            else:
                risk_format = low_risk_format

            worksheet.write(row, 0, partner.name or '')
            worksheet.write(row, 1, dict(partner._fields['risk_level'].selection).get(partner.risk_level, ''), risk_format)
            worksheet.write(row, 2, partner.inherent_risk or 0)
            worksheet.write(row, 3, partner.residual_risk or 0)
            worksheet.write(row, 4, 'Yes' if partner.edd_required else 'No')
            worksheet.write(row, 5, partner.last_assessment_date.strftime('%Y-%m-%d') if partner.last_assessment_date else '')
            worksheet.write(row, 6, partner.next_review_date.strftime('%Y-%m-%d') if partner.next_review_date else '')
            worksheet.write(row, 7, dict(partner._fields['sanctions_status'].selection).get(partner.sanctions_status, ''))
            row += 1

        # Auto-fit columns
        worksheet.set_column(0, 0, 30)  # Customer name
        worksheet.set_column(1, 1, 12)  # Risk level
        worksheet.set_column(2, 3, 13)  # Risk scores
        worksheet.set_column(4, 4, 12)  # EDD
        worksheet.set_column(5, 6, 15)  # Dates
        worksheet.set_column(7, 7, 15)  # Sanctions status

        workbook.close()
        output.seek(0)
        xlsx_data = output.read()
        output.close()

        # Create attachment
        filename = f'customer_risk_summary_{fields.Date.today()}.xlsx'
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(xlsx_data),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def _export_excel_basic(self):
        """Export BASIC report as Excel with 3 sheets matching nex-systems schema."""
        try:
            import xlsxwriter
            from io import BytesIO
        except ImportError:
            raise UserError(_('xlsxwriter library not installed'))

        # Build partner domain using advanced filters if enabled
        if self.query_type == 'advanced':
            domain = self._build_advanced_filter_domain()
        else:
            domain = [
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to)
            ]
            if self.partner_ids:
                domain = [('id', 'in', self.partner_ids.ids)]

        partners = self.env['res.partner'].search(domain)

        if not partners:
            raise UserError(_('No customers found for the specified criteria'))

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1})

        # Sheet 1: Report Customer Transaction
        tx_sheet = workbook.add_worksheet('Report Customer Transaction')
        tx_headers = [
            'Transaction Date', 'Amount', 'Customer Name', 'Transaction Type',
            'Products', 'Branch name', 'PEP Status (yes/no)',
            'Resident vs/non Resident', 'Country'
        ]
        for col, header in enumerate(tx_headers):
            tx_sheet.write(0, col, header, header_format)

        tx_row = 1
        for partner in partners:
            # Build transaction domain with optional filters
            tx_domain = self._build_transaction_filter_domain()
            tx_domain.extend([
                ('partner_id', '=', partner.id),
                ('state', '=', 'posted')
            ])
            moves = self.env['account.move'].search(tx_domain)
            for move in moves:
                tx_sheet.write(tx_row, 0, move.date.strftime('%Y-%m-%d') if move.date else '')
                tx_sheet.write(tx_row, 1, move.amount_total or 0)
                tx_sheet.write(tx_row, 2, partner.name or '')
                tx_sheet.write(tx_row, 3, move.move_type.replace('_', ' ').upper() if move.move_type else '')
                tx_sheet.write(tx_row, 4, '')
                tx_sheet.write(tx_row, 5, '')
                tx_sheet.write(tx_row, 6, 'Yes' if partner.pep_status else 'No')
                tx_sheet.write(tx_row, 7, 'Resident' if partner.country_id and partner.country_id == self.company_id.country_id else 'Non Resident')
                tx_sheet.write(tx_row, 8, partner.country_id.code if partner.country_id else '')
                tx_row += 1

        tx_sheet.set_column(0, 0, 15)
        tx_sheet.set_column(1, 1, 12)
        tx_sheet.set_column(2, 2, 30)
        tx_sheet.set_column(3, 8, 18)

        # Sheet 2: All Customer Individual
        ind_sheet = workbook.add_worksheet('All Customer Individual')
        ind_headers = [
            'Customer Name', 'Date Of Registration', 'Date Of Birth', 'Country Of Birth',
            'Nationality', 'Gender', 'ID Number', 'Residency Status', 'Resident Country',
            'Source Of Funds', 'Occupation', 'Employer', 'PEP Status', 'Address',
            'City', 'Country', 'Phone', 'Email', 'Risk Level'
        ]
        for col, header in enumerate(ind_headers):
            ind_sheet.write(0, col, header, header_format)

        ind_row = 1
        individuals = partners.filtered(lambda p: not p.is_company)
        for partner in individuals:
            ind_sheet.write(ind_row, 0, partner.name or '')
            ind_sheet.write(ind_row, 1, partner.create_date.strftime('%Y-%m-%d') if partner.create_date else '')
            ind_sheet.write(ind_row, 2, '')
            ind_sheet.write(ind_row, 3, '')
            ind_sheet.write(ind_row, 4, partner.country_id.code if partner.country_id else '')
            ind_sheet.write(ind_row, 5, '')
            ind_sheet.write(ind_row, 6, partner.vat or '')
            ind_sheet.write(ind_row, 7, 'Resident' if partner.country_id and partner.country_id == self.company_id.country_id else 'Non-Resident')
            ind_sheet.write(ind_row, 8, partner.country_id.code if partner.country_id else '')
            ind_sheet.write(ind_row, 9, '')
            ind_sheet.write(ind_row, 10, '')
            ind_sheet.write(ind_row, 11, '')
            ind_sheet.write(ind_row, 12, 'Yes' if partner.pep_status else 'No')
            ind_sheet.write(ind_row, 13, partner.street or '')
            ind_sheet.write(ind_row, 14, partner.city or '')
            ind_sheet.write(ind_row, 15, partner.country_id.code if partner.country_id else '')
            ind_sheet.write(ind_row, 16, partner.phone or '')
            ind_sheet.write(ind_row, 17, partner.email or '')
            ind_sheet.write(ind_row, 18, partner.risk_level.upper() if partner.risk_level else '')
            ind_row += 1

        for i in range(len(ind_headers)):
            ind_sheet.set_column(i, i, 18)

        # Sheet 3: All Customer Corporates
        corp_sheet = workbook.add_worksheet('All Customer Corporates')
        corp_headers = [
            'Registration Date', 'Registration Number', 'Corporate Name', 'Entity Type',
            'Country Of Incorporation', 'Tax Number', 'License Number', 'Sector',
            'Source Of Funds', 'Nature Of Business', 'Address', 'City', 'Country',
            'Phone', 'Email', 'Risk Level'
        ]
        for col, header in enumerate(corp_headers):
            corp_sheet.write(0, col, header, header_format)

        corp_row = 1
        corporates = partners.filtered(lambda p: p.is_company)
        for partner in corporates:
            corp_sheet.write(corp_row, 0, partner.create_date.strftime('%Y-%m-%d') if partner.create_date else '')
            corp_sheet.write(corp_row, 1, partner.vat or '')
            corp_sheet.write(corp_row, 2, partner.name or '')
            corp_sheet.write(corp_row, 3, '')
            corp_sheet.write(corp_row, 4, partner.country_id.code if partner.country_id else '')
            corp_sheet.write(corp_row, 5, partner.vat or '')
            corp_sheet.write(corp_row, 6, '')
            corp_sheet.write(corp_row, 7, '')
            corp_sheet.write(corp_row, 8, '')
            corp_sheet.write(corp_row, 9, '')
            corp_sheet.write(corp_row, 10, partner.street or '')
            corp_sheet.write(corp_row, 11, partner.city or '')
            corp_sheet.write(corp_row, 12, partner.country_id.code if partner.country_id else '')
            corp_sheet.write(corp_row, 13, partner.phone or '')
            corp_sheet.write(corp_row, 14, partner.email or '')
            corp_sheet.write(corp_row, 15, partner.risk_level.upper() if partner.risk_level else '')
            corp_row += 1

        for i in range(len(corp_headers)):
            corp_sheet.set_column(i, i, 18)

        workbook.close()
        output.seek(0)
        xlsx_data = output.read()
        output.close()

        filename = f'Standard_Report_{fields.Date.today()}.xlsx'
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(xlsx_data),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


    # goAML Export Methods
    def _export_goaml_sar(self):
        """Export SAR in goAML XML format."""
        xml_content = self._generate_goaml_xml('SAR')
        return self._download_goaml_file(xml_content, 'sar')

    def _export_goaml_str(self):
        """Export STR in goAML XML format."""
        xml_content = self._generate_goaml_xml('STR')
        return self._download_goaml_file(xml_content, 'str')

    def _generate_goaml_xml(self, report_type, partners=None, threshold=None):
        """Generate goAML XML structure for various report types."""
        from xml.etree import ElementTree as ET

        # Root element
        root = ET.Element('report')
        root.set('xmlns', 'http://www.goaml.org/report')
        root.set('type', report_type)

        # Report header
        header = ET.SubElement(root, 'report_header')
        ET.SubElement(header, 'report_code').text = f'{report_type}-{fields.Date.today()}'
        ET.SubElement(header, 'submission_date').text = fields.Datetime.now().isoformat()
        ET.SubElement(header, 'reporting_entity').text = self.company_id.name

        # For case-based reports (SAR, STR)
        if self.case_ids:
            for case in self.case_ids:
                case_elem = ET.SubElement(root, 'case')
                ET.SubElement(case_elem, 'case_number').text = case.name
                ET.SubElement(case_elem, 'case_type').text = case.case_type
                ET.SubElement(case_elem, 'opened_date').text = case.opened_date.isoformat() if case.opened_date else ''

                # Subject (partner)
                if case.partner_id:
                    subject = ET.SubElement(case_elem, 'subject')
                    ET.SubElement(subject, 'name').text = case.partner_id.name or ''
                    ET.SubElement(subject, 'type').text = 'legal_person' if case.partner_id.is_company else 'natural_person'
                    if case.partner_id.country_id:
                        ET.SubElement(subject, 'country').text = case.partner_id.country_id.code or ''

                # Transactions
                for move in case.move_ids:
                    trans = ET.SubElement(case_elem, 'transaction')
                    ET.SubElement(trans, 'date').text = move.date.isoformat() if move.date else ''
                    ET.SubElement(trans, 'amount').text = str(move.amount_total or 0)
                    ET.SubElement(trans, 'currency').text = move.currency_id.name if move.currency_id else ''

                # Narrative
                if self.include_narrative and case.investigation_notes:
                    narrative = ET.SubElement(case_elem, 'narrative')
                    narrative.text = case.investigation_notes

        # For partner-based reports (DPMSR, PNMR, CNMR, AIF, AIFT, ECDD)
        elif partners:
            activity = ET.SubElement(root, 'activity')
            for partner in partners:
                subject = ET.SubElement(activity, 'subject')
                ET.SubElement(subject, 'name').text = partner.name or ''
                ET.SubElement(subject, 'type').text = 'legal_person' if partner.is_company else 'natural_person'
                ET.SubElement(subject, 'customer_id').text = str(partner.id)

                if partner.country_id:
                    ET.SubElement(subject, 'country').text = partner.country_id.code or ''

                if partner.pep_status:
                    ET.SubElement(subject, 'pep_status').text = 'true'

                if partner.sanctions_status:
                    ET.SubElement(subject, 'sanctions_status').text = partner.sanctions_status

                if partner.risk_level:
                    ET.SubElement(subject, 'risk_level').text = partner.risk_level

                if threshold and report_type == 'AIFT':
                    ET.SubElement(subject, 'threshold_amount').text = str(threshold)

        # Convert to string
        return ET.tostring(root, encoding='utf-8', xml_declaration=True)

    def _download_goaml_file(self, xml_content, report_type):
        """Create downloadable goAML XML file."""
        filename = f'{report_type}_{fields.Date.today()}.xml'
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(xml_content),
            'mimetype': 'application/xml',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
