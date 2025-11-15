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
    PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from odoo import api, models, _

_logger = logging.getLogger(__name__)


class CasePdfReport(models.AbstractModel):
    """Case PDF Report Generator."""
    _name = 'report.nexaml.case_pdf_report'
    _description = 'Case PDF Report'

    def _get_risk_color(self, level):
        """Get color for risk level."""
        if level == 'high' or level == 'critical':
            return colors.HexColor('#991b1b')  # red-800
        elif level == 'medium':
            return colors.HexColor('#92400e')  # yellow-800
        else:
            return colors.HexColor('#065f46')  # green-800

    def _get_status_color(self, state):
        """Get color for case status."""
        status_colors = {
            'open': colors.HexColor('#3b82f6'),  # blue
            'investigating': colors.HexColor('#8b5cf6'),  # purple
            'under_review': colors.HexColor('#f59e0b'),  # amber
            'pending_info': colors.HexColor('#ef4444'),  # red
            'resolved_approved': colors.HexColor('#10b981'),  # green
            'resolved_rejected': colors.HexColor('#dc2626'),  # red-600
            'closed': colors.HexColor('#6b7280'),  # gray
        }
        return status_colors.get(state, colors.grey)

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get values for report."""
        docs = self.env['aml.case'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'aml.case',
            'docs': docs,
            'data': data,
        }

    def generate_pdf(self, case):
        """Generate PDF for a single case."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )

        # Container for PDF elements
        story = []

        # Styles
        styles = getSampleStyleSheet()
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
        normal_style = styles['Normal']

        # Title
        story.append(Paragraph(f"Case Report: {case.name}", title_style))
        story.append(Spacer(1, 0.2*inch))

        # Case Information Table
        story.append(Paragraph("Case Information", heading_style))
        case_info = [
            ['Case Number:', case.name],
            ['Case Type:', dict(case._fields['case_type'].selection).get(case.case_type, case.case_type)],
            ['Status:', dict(case._fields['state'].selection).get(case.state, case.state)],
            ['Priority:', dict(case._fields['priority'].selection).get(case.priority, case.priority).upper()],
            ['Customer:', case.partner_id.name or 'N/A'],
            ['Assigned To:', case.assigned_to.name if case.assigned_to else 'Unassigned'],
            ['Opened Date:', case.opened_date.strftime('%Y-%m-%d %H:%M') if case.opened_date else 'N/A'],
            ['Closed Date:', case.closed_date.strftime('%Y-%m-%d %H:%M') if case.closed_date else 'N/A'],
        ]

        case_table = Table(case_info, colWidths=[2*inch, 4*inch])
        case_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(case_table)
        story.append(Spacer(1, 0.3*inch))

        # Description
        if case.description:
            story.append(Paragraph("Description", heading_style))
            story.append(Paragraph(case.description or 'N/A', normal_style))
            story.append(Spacer(1, 0.2*inch))

        # Investigation Notes
        if case.investigation_notes:
            story.append(Paragraph("Investigation Notes", heading_style))
            # Strip HTML tags for PDF
            notes_text = case.investigation_notes.replace('<p>', '').replace('</p>', '\n').replace('<br/>', '\n')
            story.append(Paragraph(notes_text or 'N/A', normal_style))
            story.append(Spacer(1, 0.2*inch))

        # Page Break before details
        story.append(PageBreak())

        # Decisions
        if case.decision_ids:
            story.append(Paragraph(f"Decisions ({len(case.decision_ids)})", heading_style))
            for decision in case.decision_ids:
                decision_data = [
                    ['Decision Type:', dict(decision._fields['decision_type'].selection).get(decision.decision_type, decision.decision_type)],
                    ['Outcome:', dict(decision._fields['outcome'].selection).get(decision.outcome, decision.outcome) if decision.outcome else 'N/A'],
                    ['Decided By:', decision.decided_by.name],
                    ['Date:', decision.decided_date.strftime('%Y-%m-%d %H:%M')],
                    ['Rationale:', decision.rationale[:200] + '...' if len(decision.rationale) > 200 else decision.rationale],
                ]
                decision_table = Table(decision_data, colWidths=[1.5*inch, 4.5*inch])
                decision_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eff6ff')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bfdbfe')),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(decision_table)
                story.append(Spacer(1, 0.15*inch))

        # Timeline
        if case.timeline_ids:
            story.append(Paragraph(f"Timeline ({len(case.timeline_ids)} events)", heading_style))
            timeline_data = [['Date', 'Event Type', 'Description']]
            for event in case.timeline_ids.sorted(lambda e: e.event_date, reverse=True)[:20]:  # Latest 20
                timeline_data.append([
                    event.event_date.strftime('%Y-%m-%d\n%H:%M'),
                    dict(event._fields['event_type'].selection).get(event.event_type, event.event_type),
                    event.description[:100] + '...' if len(event.description) > 100 else event.description
                ])

            timeline_table = Table(timeline_data, colWidths=[1.2*inch, 1.8*inch, 3*inch])
            timeline_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(timeline_table)
            story.append(Spacer(1, 0.2*inch))

        # Tasks
        if case.task_ids:
            story.append(Paragraph(f"Tasks ({len(case.task_ids)})", heading_style))
            task_data = [['Task', 'Type', 'Status', 'Assigned To', 'Due Date']]
            for task in case.task_ids:
                task_data.append([
                    task.name[:40] + '...' if len(task.name) > 40 else task.name,
                    dict(task._fields['task_type'].selection).get(task.task_type, task.task_type),
                    dict(task._fields['state'].selection).get(task.state, task.state),
                    task.assigned_to.name if task.assigned_to else 'Unassigned',
                    task.due_date.strftime('%Y-%m-%d') if task.due_date else 'N/A',
                ])

            task_table = Table(task_data, colWidths=[2*inch, 1.2*inch, 1*inch, 1.2*inch, 0.8*inch])
            task_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(task_table)

        # Build PDF
        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
