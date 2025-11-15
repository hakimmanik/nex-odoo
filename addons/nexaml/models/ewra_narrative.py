# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class EwraNarrative(models.Model):
    """EWRA report narrative sections."""
    _name = 'nexaml.ewra.narrative'
    _description = 'EWRA Narrative'

    run_id = fields.Many2one(
        'nexaml.ewra.run',
        string='EWRA Run',
        required=True,
        ondelete='cascade',
        help='Related EWRA run'
    )

    # Foreword
    foreword = fields.Html(
        string='Foreword',
        help='Compliance officer statement at the beginning of the report'
    )
    foreword_author = fields.Many2one(
        'res.users',
        string='Foreword Author',
        help='Person who wrote the foreword'
    )

    # Company Overview
    company_overview = fields.Html(
        string='Company Overview',
        help='Overview of the organization and its business'
    )

    # Methodology
    methodology = fields.Html(
        string='Methodology',
        help='Description of the risk assessment methodology'
    )

    # Conclusion
    conclusion = fields.Html(
        string='Conclusion',
        help='Summary and conclusions of the risk assessment'
    )
    conclusion_author = fields.Many2one(
        'res.users',
        string='Conclusion Author',
        help='Person who wrote the conclusion'
    )

    # Recommendations
    recommendations = fields.Html(
        string='Recommendations',
        help='Recommendations based on the assessment'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='run_id.company_id',
        store=True,
        help='Company'
    )

    @api.model
    def create_default(self, run_id):
        """Create narrative with default content."""
        company = self.env.company

        return self.create({
            'run_id': run_id,
            'foreword': _('''
<h3>Foreword</h3>
<p>This Enterprise-Wide Risk Assessment (EWRA) has been conducted to evaluate the Anti-Money Laundering (AML)
and Counter-Financing of Terrorism (CFT) risks faced by %s during the assessment period.</p>

<p>The assessment considers multiple risk factors including customer types, geographic exposure, products and
services offered, delivery channels utilized, and supplier relationships. Our evaluation follows a structured
methodology to identify inherent risks and assess the effectiveness of our control environment.</p>

<p>This report provides management and stakeholders with a comprehensive view of our risk profile and the
adequacy of our risk mitigation measures.</p>
            ''') % company.name,
            'foreword_author': self.env.user.id,
            'company_overview': _('''
<h3>Company Overview</h3>
<p><strong>Legal Name:</strong> %s</p>
<p><strong>Assessment Period:</strong> [Period will be filled automatically]</p>

<p>Our organization is committed to maintaining the highest standards of compliance with AML/CFT regulations
and continuously improving our risk management framework.</p>
            ''') % company.name,
            'methodology': _('''
<h3>Risk Assessment Methodology</h3>
<p>Our Enterprise-Wide Risk Assessment follows a structured approach:</p>

<ol>
    <li><strong>Risk Identification:</strong> Identify inherent risks across five key pillars:
        <ul>
            <li>Customer Risk</li>
            <li>Geographic Risk</li>
            <li>Products & Services Risk</li>
            <li>Delivery Channel Risk</li>
            <li>Supplier Risk</li>
        </ul>
    </li>
    <li><strong>Risk Scoring:</strong> Rate each entity as Low (1.0), Medium (2.0), or High (3.0) risk</li>
    <li><strong>Inherent Risk Calculation:</strong> Calculate weighted average risk scores</li>
    <li><strong>Control Assessment:</strong> Evaluate effectiveness of controls (0-70%)</li>
    <li><strong>Residual Risk:</strong> Calculate risk after applying controls</li>
</ol>

<h4>Risk Classifications:</h4>
<ul>
    <li><strong>Low Risk:</strong> 1.0 - 1.6</li>
    <li><strong>Medium Risk:</strong> 1.7 - 2.3</li>
    <li><strong>High Risk:</strong> 2.4 - 3.0</li>
</ul>
            '''),
            'conclusion': _('''
<h3>Conclusion</h3>
<p>Based on this comprehensive assessment, we have identified our key risk areas and evaluated the effectiveness
of our control environment. The results indicate [summary will be added based on findings].</p>

<p>We remain committed to maintaining a robust AML/CFT compliance framework and will continue to monitor and
enhance our controls as needed.</p>
            '''),
            'conclusion_author': self.env.user.id,
            'recommendations': _('''
<h3>Recommendations</h3>
<p>Based on the findings of this assessment, we recommend:</p>
<ol>
    <li>Continue enhanced monitoring of high-risk relationships</li>
    <li>Review and update policies and procedures annually</li>
    <li>Provide ongoing training to staff on AML/CFT obligations</li>
    <li>Conduct periodic reviews of customer risk classifications</li>
</ol>
            ''')
        })
