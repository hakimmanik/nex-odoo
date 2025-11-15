# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import io
import logging
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, KeepTogether, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from odoo import api, models, _

_logger = logging.getLogger(__name__)


class CustomerProfilePdfReport(models.AbstractModel):
    """Customer Profile PDF Report Generator."""
    _name = 'report.nexaml.customer_profile_pdf_report'
    _description = 'Customer Profile PDF Report'

    def _get_risk_badge_color(self, level):
        """Get background and text color for risk level."""
        if level == 'high':
            return (colors.HexColor('#fee2e2'), colors.HexColor('#991b1b'))  # red-100, red-800
        elif level == 'medium':
            return (colors.HexColor('#fef3c7'), colors.HexColor('#92400e'))  # yellow-100, yellow-800
        else:
            return (colors.HexColor('#d1fae5'), colors.HexColor('#065f46'))  # green-100, green-800

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get values for report."""
        docs = self.env['res.partner'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': docs,
            'data': data,
        }

    def generate_pdf(self, partner):
        """Generate PDF for a single customer."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )

        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#374151'),
            spaceAfter=12,
            spaceBefore=20,
        )

        story.append(Paragraph(f"Customer Profile: {partner.name}", title_style))
        story.append(Spacer(1, 0.2*inch))

        # Basic Information
        story.append(Paragraph("Basic Information", heading_style))
        basic_info = [
            ['Customer Name:', partner.name or 'N/A'],
            ['Customer Type:', 'Company' if partner.is_company else 'Individual'],
            ['Email:', partner.email or 'N/A'],
            ['Phone:', partner.phone or 'N/A'],
            ['Address:', partner.contact_address or 'N/A'],
            ['Country:', partner.country_id.name if partner.country_id else 'N/A'],
        ]

        basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(basic_table)
        story.append(Spacer(1, 0.3*inch))

        # Risk Assessment
        story.append(Paragraph("Risk Assessment", heading_style))
        risk_info = [
            ['Risk Level:', dict(partner._fields['risk_level'].selection).get(partner.risk_level, partner.risk_level).upper()],
            ['Residual Risk Score:', f"{partner.residual_risk:.2f}" if partner.residual_risk else 'N/A'],
            ['Inherent Risk Score:', f"{partner.inherent_risk:.2f}" if partner.inherent_risk else 'N/A'],
            ['EDD Required:', 'Yes' if partner.edd_required else 'No'],
            ['PEP Status:', 'Yes' if partner.pep_status else 'No'],
            ['Last Assessment:', partner.last_assessment_date.strftime('%Y-%m-%d') if partner.last_assessment_date else 'Never'],
            ['Next Review:', partner.next_review_date.strftime('%Y-%m-%d') if partner.next_review_date else 'N/A'],
        ]

        risk_table = Table(risk_info, colWidths=[2*inch, 4*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fef3c7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#fbbf24')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 0.3*inch))

        # Risk Components
        story.append(Paragraph("Risk Components", heading_style))
        components_data = [
            ['Component', 'Score'],
            ['Customer Risk (30%)', f"{partner.customer_risk:.1f}" if partner.customer_risk else 'N/A'],
            ['Geography Risk (20%)', f"{partner.geography_risk:.1f}" if partner.geography_risk else 'N/A'],
            ['Product Risk (30%)', f"{partner.product_risk:.1f}" if partner.product_risk else 'N/A'],
            ['Channel Risk (20%)', f"{partner.channel_risk:.1f}" if partner.channel_risk else 'N/A'],
        ]

        components_table = Table(components_data, colWidths=[4*inch, 2*inch])
        components_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(components_table)
        story.append(Spacer(1, 0.3*inch))

        # Sanctions Screening
        story.append(Paragraph("Sanctions Screening", heading_style))
        sanctions_info = [
            ['Status:', dict(partner._fields['sanctions_status'].selection).get(partner.sanctions_status, partner.sanctions_status).upper()],
            ['Last Screened:', partner.last_screening_date.strftime('%Y-%m-%d %H:%M') if partner.last_screening_date else 'Never'],
            ['Total Screenings:', str(partner.screening_count)],
        ]

        sanctions_table = Table(sanctions_info, colWidths=[2*inch, 4*inch])
        sanctions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(sanctions_table)
        story.append(Spacer(1, 0.3*inch))

        # Products & Services
        if partner.product_ids:
            story.append(Paragraph("Products & Services", heading_style))
            products_text = ', '.join([p.name for p in partner.product_ids])
            story.append(Paragraph(products_text, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))

        # Controls
        if partner.control_ids:
            story.append(Paragraph("Applied Controls", heading_style))
            controls_data = [['Control', 'Mitigation Factor']]
            for control in partner.control_ids:
                controls_data.append([
                    control.name,
                    f"{control.mitigation_factor}%"
                ])

            controls_table = Table(controls_data, colWidths=[4*inch, 2*inch])
            controls_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(controls_table)
            story.append(Spacer(1, 0.2*inch))

        # Page Break
        story.append(PageBreak())

        # Screening History
        screenings = self.env['aml.screening'].search([
            ('partner_id', '=', partner.id)
        ], limit=10, order='screening_date desc')

        if screenings:
            story.append(Paragraph(f"Recent Screening History ({len(screenings)})", heading_style))
            screening_data = [['Date', 'Result', 'Matches', 'Reviewed']]
            for screening in screenings:
                screening_data.append([
                    screening.screening_date.strftime('%Y-%m-%d %H:%M'),
                    dict(screening._fields['result'].selection).get(screening.result, screening.result),
                    str(screening.match_count),
                    'Yes' if screening.reviewed else 'No'
                ])

            screening_table = Table(screening_data, colWidths=[1.8*inch, 1.5*inch, 1*inch, 1*inch])
            screening_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(screening_table)

        # Build PDF
        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
