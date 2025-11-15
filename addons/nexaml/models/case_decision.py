# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import logging
from datetime import timedelta

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class CaseDecision(models.Model):
    """Case decision tracking."""
    _name = 'aml.case.decision'
    _description = 'Case Decision'
    _order = 'decided_date desc, id desc'

    case_id = fields.Many2one(
        'aml.case',
        string='Case',
        required=True,
        ondelete='cascade',
        help='Related case'
    )
    decision_type = fields.Selection(
        [('approve', 'Approve'),
         ('reject', 'Reject'),
         ('escalate', 'Escalate'),
         ('request_info', 'Request Information')],
        string='Decision Type',
        required=True,
        help='Type of decision made'
    )
    outcome = fields.Selection(
        [('false_positive', 'False Positive'),
         ('true_positive', 'True Positive'),
         ('cleared', 'Cleared'),
         ('risk_accepted', 'Risk Accepted'),
         ('relationship_terminated', 'Relationship Terminated'),
         ('ongoing_monitoring', 'Ongoing Monitoring')],
        string='Outcome',
        help='Final outcome of the decision'
    )
    rationale = fields.Text(
        string='Rationale',
        required=True,
        help='Reasoning behind the decision'
    )
    decided_by = fields.Many2one(
        'res.users',
        string='Decided By',
        required=True,
        default=lambda self: self.env.user,
        help='User who made the decision'
    )
    decided_date = fields.Datetime(
        string='Decision Date',
        required=True,
        default=fields.Datetime.now,
        help='When the decision was made'
    )
    reviewed_by = fields.Many2one(
        'res.users',
        string='Reviewed By',
        help='User who reviewed/approved the decision'
    )
    reviewed_date = fields.Datetime(
        string='Review Date',
        help='When the decision was reviewed'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        help='Company'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to trigger automated impact processing."""
        decisions = super(CaseDecision, self).create(vals_list)

        for decision in decisions:
            decision._process_decision_impact()

        return decisions

    def _process_decision_impact(self):
        """Process automated impacts when decision is made."""
        self.ensure_one()

        # 1. Log timeline event
        self.case_id.timeline_ids.create({
            'case_id': self.case_id.id,
            'event_type': 'decision_made',
            'description': _('Decision made: %s - %s') % (
                dict(self._fields['decision_type'].selection).get(self.decision_type),
                dict(self._fields['outcome'].selection).get(self.outcome) if self.outcome else 'No outcome'
            ),
            'details': {
                'decision_id': self.id,
                'decision_type': self.decision_type,
                'outcome': self.outcome,
                'decided_by': self.decided_by.name
            }
        })

        # 2. Update partner status for screening cases
        if self.case_id.case_type in ['sanctions', 'pep', 'adverse_media', 'screening']:
            self._process_screening_impact()

        # 3. Auto-update case state based on decision type
        if self.decision_type == 'approve' and self.outcome:
            if self.outcome in ['false_positive', 'cleared']:
                self.case_id.write({'state': 'resolved_approved'})
            elif self.outcome in ['true_positive', 'ongoing_monitoring']:
                self.case_id.write({'state': 'under_review'})
        elif self.decision_type == 'reject':
            self.case_id.write({'state': 'resolved_rejected'})
        elif self.decision_type == 'escalate':
            # Create escalation task
            self._create_escalation_task()
        elif self.decision_type == 'request_info':
            self.case_id.write({'state': 'pending_info'})
            self._create_info_request_task()

        # 4. Recalculate partner risk
        if self.case_id.partner_id:
            self.case_id.partner_id._compute_risk()
            _logger.info('Risk recalculated for partner %s after decision on case %s',
                       self.case_id.partner_id.name, self.case_id.name)

    def _process_screening_impact(self):
        """Process screening case specific impacts."""
        self.ensure_one()

        partner = self.case_id.partner_id
        if not partner:
            return

        # Update related screening records linked to this case
        # Find screenings linked via timeline
        timeline_entries = self.env['aml.case.timeline'].search([
            ('case_id', '=', self.case_id.id),
            ('event_type', '=', 'other')
        ])

        screening_ids = []
        for timeline in timeline_entries:
            if timeline.details and 'screening_id' in str(timeline.details):
                try:
                    import json
                    details = json.loads(timeline.details) if isinstance(timeline.details, str) else timeline.details
                    if 'screening_id' in details:
                        screening_ids.append(details['screening_id'])
                except:
                    pass

        screenings = self.env['aml.screening'].browse(screening_ids) if screening_ids else self.env['aml.screening']

        if self.outcome == 'false_positive':
            # Mark screenings as false positive
            for screening in screenings:
                screening.sudo().write({
                    'status': 'false_positive',
                    'reviewed_by': self.decided_by.id,
                    'review_date': self.decided_date,
                    'review_notes': self.rationale
                })
        elif self.outcome == 'cleared':
            # Mark screenings as clear
            for screening in screenings:
                screening.sudo().write({
                    'status': 'clear',
                    'reviewed_by': self.decided_by.id,
                    'review_date': self.decided_date,
                    'review_notes': self.rationale
                })

        if self.outcome == 'true_positive':
            # Confirmed sanctions match
            partner.sanctions_status = 'match'
            partner.message_post(
                body=_('Screening case %s: Confirmed Match. Enhanced monitoring required.') % self.case_id.name,
                subject=_('Confirmed Sanctions Match'),
                message_type='notification',
            )
            _logger.info('Partner %s sanctions status set to "match" (confirmed)', partner.name)

            # Create EDD task
            self.env['aml.case.task'].create({
                'case_id': self.case_id.id,
                'name': _('Enhanced Due Diligence Required'),
                'task_type': 'document_review',
                'priority': 'high',
                'assigned_to': self.case_id.assigned_to.id if self.case_id.assigned_to else self.env.user.id,
                'due_date': fields.Date.today() + timedelta(days=7),
                'notes': _('Customer confirmed as sanctions match. Conduct enhanced due diligence and review relationship.')
            })

        elif self.outcome == 'false_positive':
            # Set partner status to false positive
            partner.sanctions_status = 'false_positive'
            partner.message_post(
                body=_('Screening case %s: False Positive. Sanctions match dismissed.') % self.case_id.name,
                subject=_('False Positive'),
                message_type='notification',
            )
            _logger.info('Partner %s sanctions status set to false_positive (case %s)',
                       partner.name, self.case_id.name)

        elif self.outcome == 'cleared':
            # Set partner status to cleared
            partner.sanctions_status = 'clear'
            partner.message_post(
                body=_('Screening case %s: Cleared. No sanctions risk identified.') % self.case_id.name,
                subject=_('Cleared'),
                message_type='notification',
            )
            _logger.info('Partner %s sanctions status cleared (case %s)',
                       partner.name, self.case_id.name)

        elif self.outcome == 'ongoing_monitoring':
            # Keep as match but create monitoring task
            partner.sanctions_status = 'match'
            self.env['aml.case.task'].create({
                'case_id': self.case_id.id,
                'name': _('Ongoing Monitoring Required'),
                'task_type': 'risk_analysis',
                'priority': 'medium',
                'assigned_to': self.case_id.assigned_to.id if self.case_id.assigned_to else self.env.user.id,
                'due_date': fields.Date.today() + timedelta(days=30),
                'notes': _('Continue monitoring customer transactions and activities.')
            })

        elif self.outcome == 'relationship_terminated':
            # Mark customer inactive
            partner.message_post(
                body=_('Screening case %s: Relationship Terminated due to sanctions match.') % self.case_id.name,
                subject=_('Relationship Terminated'),
                message_type='notification',
            )

    def _create_escalation_task(self):
        """Create task for escalation."""
        self.env['aml.case.task'].create({
            'case_id': self.case_id.id,
            'name': _('Case Escalated - Senior Review Required'),
            'task_type': 'approval_required',
            'priority': 'high',
            'assigned_to': self.env.ref('base.user_admin').id,  # Escalate to admin
            'due_date': fields.Date.today() + timedelta(days=3),
            'notes': _('This case has been escalated for senior review. Decision: %s\nRationale: %s') % (
                dict(self._fields['decision_type'].selection).get(self.decision_type),
                self.rationale
            )
        })
        _logger.info('Case %s escalated, task created', self.case_id.name)

    def _create_info_request_task(self):
        """Create task for information request."""
        self.env['aml.case.task'].create({
            'case_id': self.case_id.id,
            'name': _('Additional Information Required'),
            'task_type': 'data_collection',
            'priority': 'high',
            'assigned_to': self.case_id.assigned_to.id if self.case_id.assigned_to else self.env.user.id,
            'due_date': fields.Date.today() + timedelta(days=5),
            'notes': _('Additional information requested. Rationale: %s') % self.rationale
        })
        _logger.info('Information request task created for case %s', self.case_id.name)
