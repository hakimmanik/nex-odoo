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
    output_format = fields.Selection(
        [('pdf', 'PDF'),
         ('xlsx', 'Excel'),
         ('goaml', 'goAML XML')],
        string='Output Format',
        required=True,
        default='pdf',
        help='Report output format'
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

    @api.onchange('report_type')
    def _onchange_report_type(self):
        """Update fields based on report type."""
        if self.report_type in ('sar', 'str'):
            # SAR/STR requires case selection
            pass
        elif self.report_type == 'risk':
            # Risk report needs partners
            pass

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
        elif self.report_type == 'periodic':
            return self._generate_periodic_summary()
        elif self.report_type == 'risk':
            return self._generate_risk_summary()

        raise UserError(_('Unknown report type'))

    def _generate_sar(self):
        """Generate Suspicious Activity Report."""
        if not self.case_ids:
            raise UserError(_('Please select at least one case for SAR report'))

        if self.output_format == 'goaml':
            return self._export_goaml_sar()
        elif self.output_format == 'xlsx':
            return self._export_excel_sar()
        else:
            return self._export_pdf_sar()

    def _generate_str(self):
        """Generate Suspicious Transaction Report."""
        if not self.case_ids:
            raise UserError(_('Please select at least one case for STR report'))

        if self.output_format == 'goaml':
            return self._export_goaml_str()
        elif self.output_format == 'xlsx':
            return self._export_excel_str()
        else:
            return self._export_pdf_str()

    def _generate_periodic_summary(self):
        """Generate Periodic Compliance Summary."""
        if self.output_format == 'xlsx':
            return self._export_excel_periodic()
        else:
            return self._export_pdf_periodic()

    def _generate_risk_summary(self):
        """Generate Customer Risk Summary."""
        if self.output_format == 'xlsx':
            return self._export_excel_risk()
        else:
            return self._export_pdf_risk()

    # PDF Export Methods
    def _export_pdf_sar(self):
        """Export SAR as PDF."""
        return self.env.ref('nexaml.action_report_sar').report_action(self)

    def _export_pdf_str(self):
        """Export STR as PDF."""
        return self.env.ref('nexaml.action_report_str').report_action(self)

    def _export_pdf_periodic(self):
        """Export Periodic Summary as PDF."""
        return self.env.ref('nexaml.action_report_periodic').report_action(self)

    def _export_pdf_risk(self):
        """Export Risk Summary as PDF."""
        return self.env.ref('nexaml.action_report_risk').report_action(self)

    # Excel Export Methods
    def _export_excel_sar(self):
        """Export SAR as Excel."""
        # TODO: Implement Excel export
        raise UserError(_('Excel export for SAR not yet implemented'))

    def _export_excel_str(self):
        """Export STR as Excel."""
        # TODO: Implement Excel export
        raise UserError(_('Excel export for STR not yet implemented'))

    def _export_excel_periodic(self):
        """Export Periodic Summary as Excel."""
        # TODO: Implement Excel export
        raise UserError(_('Excel export for Periodic Summary not yet implemented'))

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

    # goAML Export Methods
    def _export_goaml_sar(self):
        """Export SAR in goAML XML format."""
        xml_content = self._generate_goaml_xml('SAR')
        return self._download_goaml_file(xml_content, 'sar')

    def _export_goaml_str(self):
        """Export STR in goAML XML format."""
        xml_content = self._generate_goaml_xml('STR')
        return self._download_goaml_file(xml_content, 'str')

    def _generate_goaml_xml(self, report_type):
        """Generate goAML XML structure."""
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

        # Cases
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
