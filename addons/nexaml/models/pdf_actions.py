# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import base64
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CasePdfAction(models.TransientModel):
    """Action to generate Case PDF."""
    _name = 'aml.case.pdf.action'
    _description = 'Generate Case PDF'

    case_id = fields.Many2one(
        'aml.case',
        string='Case',
        required=True,
        default=lambda self: self.env.context.get('active_id')
    )

    def action_generate_pdf(self):
        """Generate and download PDF."""
        self.ensure_one()

        # Get the PDF report generator
        report_model = self.env['report.nexaml.case_pdf_report']

        try:
            # Generate PDF
            pdf_content = report_model.generate_pdf(self.case_id)

            # Create attachment
            filename = f"Case_{self.case_id.name}.pdf"
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'res_model': 'aml.case',
                'res_id': self.case_id.id,
                'mimetype': 'application/pdf'
            })

            # Return download action
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }
        except Exception as e:
            _logger.error(f"Error generating Case PDF: {str(e)}")
            raise UserError(_('Error generating PDF: %s') % str(e))


class CustomerProfilePdfAction(models.TransientModel):
    """Action to generate Customer Profile PDF."""
    _name = 'res.partner.pdf.action'
    _description = 'Generate Customer Profile PDF'

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        default=lambda self: self.env.context.get('active_id')
    )

    def action_generate_pdf(self):
        """Generate and download PDF."""
        self.ensure_one()

        # Get the PDF report generator
        report_model = self.env['report.nexaml.customer_profile_pdf_report']

        try:
            # Generate PDF
            pdf_content = report_model.generate_pdf(self.partner_id)

            # Create attachment
            filename = f"Customer_Profile_{self.partner_id.name.replace(' ', '_')}.pdf"
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'res_model': 'res.partner',
                'res_id': self.partner_id.id,
                'mimetype': 'application/pdf'
            })

            # Return download action
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }
        except Exception as e:
            _logger.error(f"Error generating Customer Profile PDF: {str(e)}")
            raise UserError(_('Error generating PDF: %s') % str(e))


class EwraPdfAction(models.TransientModel):
    """Action to generate EWRA PDF."""
    _name = 'nexaml.ewra.pdf.action'
    _description = 'Generate EWRA PDF'

    run_id = fields.Many2one(
        'nexaml.ewra.run',
        string='EWRA Run',
        required=True,
        default=lambda self: self.env.context.get('active_id')
    )

    def action_generate_pdf(self):
        """Generate and download PDF."""
        self.ensure_one()

        # Get the PDF report generator
        report_model = self.env['report.nexaml.ewra_pdf_report']

        try:
            # Generate PDF
            pdf_content = report_model.generate_pdf(self.run_id)

            # Create attachment
            filename = f"EWRA_{self.run_id.name}.pdf"
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'res_model': 'nexaml.ewra.run',
                'res_id': self.run_id.id,
                'mimetype': 'application/pdf'
            })

            # Return download action
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }
        except Exception as e:
            _logger.error(f"Error generating EWRA PDF: {str(e)}")
            raise UserError(_('Error generating PDF: %s') % str(e))
