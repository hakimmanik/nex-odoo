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
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class EwraPdfReport(models.AbstractModel):
    """EWRA PDF Report Generator."""
    _name = 'report.nexaml.ewra_pdf_report'
    _description = 'EWRA PDF Report'

    def _get_risk_color(self, level):
        """Get color for risk level."""
        if level == 'high':
            return colors.HexColor('#dc2626')  # red-600
        elif level == 'medium':
            return colors.HexColor('#f59e0b')  # amber-500
        else:
            return colors.HexColor('#10b981')  # green-500

    def _create_risk_distribution_chart(self, pillar):
        """Create a risk distribution pie chart for a pillar."""
        drawing = Drawing(300, 200)

        # Pie chart
        pie = Pie()
        pie.x = 100
        pie.y = 50
        pie.width = 120
        pie.height = 120
        pie.data = [pillar.low_pct or 0, pillar.medium_pct or 0, pillar.high_pct or 0]
        pie.labels = [f'Low\n{pillar.low_pct:.0f}%', f'Med\n{pillar.medium_pct:.0f}%', f'High\n{pillar.high_pct:.0f}%']
        pie.slices.strokeWidth = 0.5
        pie.slices[0].fillColor = colors.HexColor('#10b981')  # green
        pie.slices[1].fillColor = colors.HexColor('#f59e0b')  # amber
        pie.slices[2].fillColor = colors.HexColor('#dc2626')  # red

        drawing.add(pie)
        return drawing

    def _create_risk_scores_chart(self, run):
        """Create bar chart comparing inherent vs residual risk scores."""
        drawing = Drawing(400, 250)

        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.height = 150
        chart.width = 300

        # Data: inherent and residual scores for each pillar
        inherent_scores = []
        residual_scores = []
        labels = []

        for pillar in run.pillar_ids.sorted('sequence'):
            labels.append(dict(pillar._fields['pillar'].selection).get(pillar.pillar, pillar.pillar)[:10])
            inherent_scores.append(pillar.inherent_score)
            residual_scores.append(pillar.residual_score)

        chart.data = [inherent_scores, residual_scores]
        chart.categoryAxis.categoryNames = labels
        chart.categoryAxis.labels.angle = 30
        chart.categoryAxis.labels.fontSize = 8
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 3
        chart.valueAxis.valueStep = 0.5

        chart.bars[0].fillColor = colors.HexColor('#3b82f6')  # blue - inherent
        chart.bars[1].fillColor = colors.HexColor('#10b981')  # green - residual

        drawing.add(chart)

        # Legend
        legend_y = 210
        drawing.add(Rect(50, legend_y, 15, 10, fillColor=colors.HexColor('#3b82f6'), strokeColor=None))
        drawing.add(String(70, legend_y + 3, 'Inherent Risk', fontSize=9))
        drawing.add(Rect(180, legend_y, 15, 10, fillColor=colors.HexColor('#10b981'), strokeColor=None))
        drawing.add(String(200, legend_y + 3, 'Residual Risk', fontSize=9))

        return drawing

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get values for report."""
        docs = self.env['nexaml.ewra.run'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'nexaml.ewra.run',
            'docs': docs,
            'data': data,
        }

    def generate_pdf(self, run):
        """Generate comprehensive EWRA PDF."""
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

        # Custom Styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=40,
            alignment=TA_CENTER
        )
        heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=12,
            spaceBefore=24,
        )
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#374151'),
            spaceAfter=10,
            spaceBefore=16,
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY
        )

        # ========== COVER PAGE ==========
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(run.company_id.name or 'Organization Name', title_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Enterprise-Wide Risk Assessment", title_style))
        story.append(Paragraph(f"Assessment Period: {run.period_start.strftime('%Y-%m-%d')} to {run.period_end.strftime('%Y-%m-%d')}", subtitle_style))
        story.append(Spacer(1, 1*inch))

        # Report metadata table
        meta_data = [
            ['EWRA ID:', run.name],
            ['Status:', dict(run._fields['status'].selection).get(run.status, run.status).upper()],
            ['Overall Risk Level:', dict(run._fields['overall_risk_level'].selection).get(run.overall_risk_level, run.overall_risk_level).upper()],
            ['Generated:', fields.Datetime.now().strftime('%Y-%m-%d %H:%M')],
        ]
        if run.approved_by:
            meta_data.append(['Approved By:', run.approved_by.name])
            meta_data.append(['Approved Date:', run.approved_date.strftime('%Y-%m-%d %H:%M') if run.approved_date else 'N/A'])

        meta_table = Table(meta_data, colWidths=[2.5*inch, 3.5*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e5e7eb')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#9ca3af')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(meta_table)

        story.append(PageBreak())

        # ========== TABLE OF CONTENTS ==========
        story.append(Paragraph("Table of Contents", heading1_style))
        story.append(Spacer(1, 0.2*inch))

        toc_items = [
            "1. Executive Summary",
            "2. Foreword",
            "3. Company Overview",
            "4. Methodology",
            "5. Risk Assessment Results",
            "   5.1 Overall Risk Profile",
            "   5.2 Customer Risk",
            "   5.3 Geography Risk",
            "   5.4 Products & Services Risk",
            "   5.5 Delivery Channel Risk",
            "   5.6 Supplier Risk",
            "6. Control Environment",
            "7. Conclusion",
            "8. Appendix: Settings Snapshot"
        ]

        for item in toc_items:
            story.append(Paragraph(item, normal_style))
            story.append(Spacer(1, 0.1*inch))

        story.append(PageBreak())

        # ========== EXECUTIVE SUMMARY ==========
        story.append(Paragraph("1. Executive Summary", heading1_style))
        summary_text = f"""
This Enterprise-Wide Risk Assessment covers the period from {run.period_start.strftime('%B %d, %Y')} to
{run.period_end.strftime('%B %d, %Y')}. The assessment evaluates Anti-Money Laundering (AML) and
Counter-Financing of Terrorism (CFT) risks across five key risk pillars.
<br/><br/>
<b>Overall Risk Assessment:</b><br/>
• Overall Inherent Risk Score: {run.overall_inherent_score:.2f}/3.00<br/>
• Overall Residual Risk Score: {run.overall_residual_score:.2f}/3.00<br/>
• Overall Risk Classification: {dict(run._fields['overall_risk_level'].selection).get(run.overall_risk_level, run.overall_risk_level).upper()}<br/>
<br/>
The residual risk score reflects the effectiveness of our control environment in mitigating inherent risks.
        """
        story.append(Paragraph(summary_text, normal_style))
        story.append(Spacer(1, 0.2*inch))

        # Overall risk scores table
        overall_summary = [
            ['Risk Pillar', 'Inherent Score', 'Control %', 'Residual Score', 'Classification'],
        ]
        for pillar in run.pillar_ids.sorted('sequence'):
            overall_summary.append([
                dict(pillar._fields['pillar'].selection).get(pillar.pillar, pillar.pillar),
                f"{pillar.inherent_score:.2f}",
                f"{pillar.control_pct:.0f}%",
                f"{pillar.residual_score:.2f}",
                dict(pillar._fields['residual_label'].selection).get(pillar.residual_label, pillar.residual_label).upper()
            ])

        summary_table = Table(overall_summary, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        story.append(summary_table)

        story.append(PageBreak())

        # ========== FOREWORD ==========
        if run.narrative_id and run.narrative_id.foreword:
            story.append(Paragraph("2. Foreword", heading1_style))
            # Strip HTML for PDF
            foreword_text = run.narrative_id.foreword.replace('<p>', '').replace('</p>', '<br/><br/>').replace('<h3>', '<b>').replace('</h3>', '</b><br/>')
            story.append(Paragraph(foreword_text, normal_style))
            story.append(Spacer(1, 0.2*inch))
            if run.narrative_id.foreword_author:
                story.append(Paragraph(f"<i>— {run.narrative_id.foreword_author.name}</i>", normal_style))
            story.append(PageBreak())

        # ========== COMPANY OVERVIEW ==========
        if run.narrative_id and run.narrative_id.company_overview:
            story.append(Paragraph("3. Company Overview", heading1_style))
            overview_text = run.narrative_id.company_overview.replace('<p>', '').replace('</p>', '<br/><br/>').replace('<h3>', '<b>').replace('</h3>', '</b><br/>')
            story.append(Paragraph(overview_text, normal_style))
            story.append(PageBreak())

        # ========== METHODOLOGY ==========
        story.append(Paragraph("4. Risk Assessment Methodology", heading1_style))
        if run.narrative_id and run.narrative_id.methodology:
            method_text = run.narrative_id.methodology.replace('<p>', '').replace('</p>', '<br/><br/>').replace('<h3>', '<b>').replace('</h3>', '</b><br/>').replace('<h4>', '<b>').replace('</h4>', '</b><br/>').replace('<li>', '• ').replace('</li>', '<br/>').replace('<ul>', '').replace('</ul>', '').replace('<ol>', '').replace('</ol>', '')
            story.append(Paragraph(method_text, normal_style))
        story.append(PageBreak())

        # ========== RISK ASSESSMENT RESULTS ==========
        story.append(Paragraph("5. Risk Assessment Results", heading1_style))
        story.append(Spacer(1, 0.1*inch))

        # 5.1 Overall Risk Profile with Chart
        story.append(Paragraph("5.1 Overall Risk Profile", heading2_style))
        story.append(Paragraph(
            f"The overall residual risk score for this assessment period is <b>{run.overall_residual_score:.2f}</b>, "
            f"classified as <b>{dict(run._fields['overall_risk_level'].selection).get(run.overall_risk_level, run.overall_risk_level).upper()}</b> risk.",
            normal_style
        ))
        story.append(Spacer(1, 0.2*inch))

        # Add risk comparison chart
        story.append(self._create_risk_scores_chart(run))
        story.append(Spacer(1, 0.3*inch))

        # Individual Pillar Assessments
        for pillar in run.pillar_ids.sorted('sequence'):
            pillar_name = dict(pillar._fields['pillar'].selection).get(pillar.pillar, pillar.pillar)
            story.append(Paragraph(f"5.{pillar.sequence}. {pillar_name}", heading2_style))

            # Pillar summary table
            pillar_summary = [
                ['Metric', 'Value'],
                ['Low Risk %', f"{pillar.low_pct:.1f}%"],
                ['Medium Risk %', f"{pillar.medium_pct:.1f}%"],
                ['High Risk %', f"{pillar.high_pct:.1f}%"],
                ['Inherent Risk Score', f"{pillar.inherent_score:.2f}"],
                ['Inherent Classification', dict(pillar._fields['inherent_label'].selection).get(pillar.inherent_label, pillar.inherent_label).upper()],
                ['Control Effectiveness', f"{pillar.control_pct:.0f}%"],
                ['Control Band', dict(pillar._fields['control_band'].selection).get(pillar.control_band, pillar.control_band)],
                ['Residual Risk Score', f"{pillar.residual_score:.2f}"],
                ['Residual Classification', dict(pillar._fields['residual_label'].selection).get(pillar.residual_label, pillar.residual_label).upper()],
            ]

            pillar_table = Table(pillar_summary, colWidths=[2.5*inch, 3.5*inch])
            pillar_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
                ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(pillar_table)
            story.append(Spacer(1, 0.15*inch))

            # Add pie chart for distribution
            story.append(self._create_risk_distribution_chart(pillar))

            # Notes
            if pillar.notes:
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph("<b>Assessment Notes:</b>", normal_style))
                notes_text = pillar.notes.replace('<p>', '').replace('</p>', '<br/>').replace('<br/>', ' ')
                story.append(Paragraph(notes_text[:500], normal_style))  # Limit length

            story.append(Spacer(1, 0.2*inch))

        story.append(PageBreak())

        # ========== CONTROL ENVIRONMENT ==========
        story.append(Paragraph("6. Control Environment", heading1_style))
        control_text = """
The control environment has been assessed across all risk pillars. Control effectiveness percentages
represent the degree to which internal controls mitigate inherent risks. The maximum control effectiveness
is capped at 70%, recognizing that no control environment can eliminate risk entirely.
<br/><br/>
<b>Control Effectiveness Bands:</b><br/>
• Weak: 0-20% mitigation<br/>
• Adequate: 21-40% mitigation<br/>
• Strong: 41-55% mitigation<br/>
• Very Strong: 56-70% mitigation<br/>
        """
        story.append(Paragraph(control_text, normal_style))
        story.append(Spacer(1, 0.2*inch))

        # Control effectiveness summary
        control_summary = [['Risk Pillar', 'Control %', 'Control Band']]
        for pillar in run.pillar_ids.sorted('sequence'):
            control_summary.append([
                dict(pillar._fields['pillar'].selection).get(pillar.pillar, pillar.pillar),
                f"{pillar.control_pct:.0f}%",
                dict(pillar._fields['control_band'].selection).get(pillar.control_band, pillar.control_band)
            ])

        control_table = Table(control_summary, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        control_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(control_table)

        story.append(PageBreak())

        # ========== CONCLUSION ==========
        if run.narrative_id and run.narrative_id.conclusion:
            story.append(Paragraph("7. Conclusion", heading1_style))
            conclusion_text = run.narrative_id.conclusion.replace('<p>', '').replace('</p>', '<br/><br/>').replace('<h3>', '<b>').replace('</h3>', '</b><br/>')
            story.append(Paragraph(conclusion_text, normal_style))
            story.append(Spacer(1, 0.3*inch))

            if run.narrative_id.conclusion_author:
                story.append(Paragraph(f"<i>— {run.narrative_id.conclusion_author.name}</i>", normal_style))

            # Recommendations
            if run.narrative_id.recommendations:
                story.append(Spacer(1, 0.3*inch))
                rec_text = run.narrative_id.recommendations.replace('<p>', '').replace('</p>', '<br/><br/>').replace('<h3>', '<b>').replace('</h3>', '</b><br/>').replace('<li>', '• ').replace('</li>', '<br/>').replace('<ul>', '').replace('</ul>', '').replace('<ol>', '').replace('</ol>', '')
                story.append(Paragraph(rec_text, normal_style))

        story.append(PageBreak())

        # ========== APPENDIX: SETTINGS SNAPSHOT ==========
        if run.settings_snapshot_id:
            story.append(Paragraph("8. Appendix: Settings Snapshot", heading1_style))
            settings = run.settings_snapshot_id

            settings_data = [
                ['Setting', 'Value'],
                ['Medium Risk Threshold', f"{settings.risk_threshold_medium:.1f}"],
                ['High Risk Threshold', f"{settings.risk_threshold_high:.1f}"],
                ['Downgrade Threshold', f"{settings.downgrade_threshold}%"],
                ['Control Cap', f"{settings.cap_pct}%"],
                ['Default Control Band', dict(settings._fields['default_control_band'].selection).get(settings.default_control_band, settings.default_control_band) if settings.default_control_band else 'N/A'],
                ['EDD Threshold', dict(settings._fields['edd_threshold'].selection).get(settings.edd_threshold, settings.edd_threshold) if settings.edd_threshold else 'N/A'],
                ['Sanctions Match Threshold', f"{settings.screening_threshold:.0f}%" if settings.screening_threshold else 'N/A'],
                ['Auto-Screen New Customers', 'Yes' if settings.auto_screen_on_create else 'No'],
            ]

            settings_table = Table(settings_data, colWidths=[3*inch, 3*inch])
            settings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
                ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f9fafb')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(settings_table)

        # Signatures
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("<b>Signatures</b>", heading2_style))
        story.append(Spacer(1, 0.3*inch))

        sig_data = [
            ['Compliance Officer:', '_' * 40],
            ['Date:', '_' * 40],
        ]
        if run.approved_by:
            sig_data = [
                ['Compliance Officer:', run.approved_by.name],
                ['Date:', run.approved_date.strftime('%Y-%m-%d') if run.approved_date else '_' * 40],
            ]

        sig_table = Table(sig_data, colWidths=[2*inch, 4*inch])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(sig_table)

        # Build PDF
        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
