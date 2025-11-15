# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import logging
from datetime import timedelta

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class Case(models.Model):
    """Investigation case management."""
    _name = 'aml.case'
    _description = 'Case'
    _order = 'opened_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Case Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        help='Unique case identifier'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        ondelete='cascade',
        tracking=True,
        help='Customer being investigated'
    )
    case_type = fields.Selection(
        [('transaction', 'Transaction Monitoring'),
         ('screening', 'Sanctions Screening'),
         ('risk', 'Risk Assessment'),
         ('other', 'Other')],
        string='Case Type',
        required=True,
        default='transaction',
        tracking=True,
        help='Type of AML case'
    )
    state = fields.Selection(
        [('open', 'Open'),
         ('investigating', 'Investigating'),
         ('under_review', 'Under Review'),
         ('pending_info', 'Pending Info'),
         ('resolved_approved', 'Resolved - Approved'),
         ('resolved_rejected', 'Resolved - Rejected'),
         ('closed', 'Closed')],
        string='State',
        required=True,
        default='open',
        tracking=True,
        group_expand='_group_expand_state',
        help='Current state of the case'
    )
    priority = fields.Selection(
        [('low', 'Low'),
         ('medium', 'Medium'),
         ('high', 'High'),
         ('critical', 'Critical')],
        string='Priority',
        default='medium',
        tracking=True,
        help='Case priority level'
    )

    # Relationships
    alert_ids = fields.Many2many(
        'aml.alert',
        'case_alert_rel',
        'case_id',
        'alert_id',
        string='Related Alerts',
        help='Alerts associated with this case'
    )
    alert_count = fields.Integer(
        string='Alert Count',
        compute='_compute_alert_count',
        help='Number of related alerts'
    )
    move_ids = fields.Many2many(
        'account.move',
        'case_move_rel',
        'case_id',
        'move_id',
        string='Related Transactions',
        help='Transactions under investigation'
    )
    move_count = fields.Integer(
        string='Transaction Count',
        compute='_compute_move_count',
        help='Number of related transactions'
    )

    # Case Management
    decision_ids = fields.One2many(
        'aml.case.decision',
        'case_id',
        string='Decisions',
        help='Case decisions'
    )
    decision_count = fields.Integer(
        string='Decision Count',
        compute='_compute_decision_count',
        help='Number of decisions'
    )
    timeline_ids = fields.One2many(
        'aml.case.timeline',
        'case_id',
        string='Timeline',
        help='Case timeline events'
    )
    timeline_count = fields.Integer(
        string='Timeline Events',
        compute='_compute_timeline_count',
        help='Number of timeline events'
    )
    note_ids = fields.One2many(
        'aml.case.note',
        'case_id',
        string='Notes',
        help='Investigation notes'
    )
    note_count = fields.Integer(
        string='Note Count',
        compute='_compute_note_count',
        help='Number of notes'
    )
    task_ids = fields.One2many(
        'aml.case.task',
        'case_id',
        string='Tasks',
        help='Case tasks'
    )
    task_count = fields.Integer(
        string='Task Count',
        compute='_compute_task_count',
        help='Number of tasks'
    )

    # Assignment
    assigned_to = fields.Many2one(
        'res.users',
        string='Assigned To',
        tracking=True,
        help='User responsible for investigating this case'
    )

    # Dates
    opened_date = fields.Datetime(
        string='Opened Date',
        required=True,
        default=fields.Datetime.now,
        help='When the case was opened'
    )
    closed_date = fields.Datetime(
        string='Closed Date',
        readonly=True,
        help='When the case was closed'
    )

    # SLA Tracking
    sla_due_date = fields.Datetime(
        string='SLA Due Date',
        compute='_compute_sla_due_date',
        help='Date by which case should be resolved based on SLA'
    )
    is_overdue = fields.Boolean(
        string='Overdue',
        compute='_compute_overdue',
        help='Whether case has exceeded SLA'
    )
    days_overdue = fields.Integer(
        string='Days Overdue',
        compute='_compute_overdue',
        help='Number of days past SLA'
    )

    # Investigation Details
    description = fields.Text(
        string='Description',
        help='Initial description of the case'
    )
    investigation_notes = fields.Html(
        string='Investigation Notes',
        help='Detailed notes from investigation'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        help='Company'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate case number."""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('aml.case') or _('New')
        return super(Case, self).create(vals_list)

    def write(self, vals):
        """Override write to trigger actions based on decision and recalculate risk."""
        # Track changes for timeline
        old_values = {}
        for case in self:
            old_values[case.id] = {
                'state': case.state,
                'priority': case.priority,
                'assigned_to': case.assigned_to.id if case.assigned_to else False,
            }

        result = super(Case, self).write(vals)

        # Log timeline events for significant changes
        for case in self:
            old = old_values.get(case.id, {})

            # State changed
            if 'state' in vals and old.get('state') != vals['state']:
                case.timeline_ids.create({
                    'case_id': case.id,
                    'event_type': 'status_changed',
                    'description': _('Status changed from %s to %s') % (
                        dict(case._fields['state'].selection).get(old.get('state'), old.get('state')),
                        dict(case._fields['state'].selection).get(vals['state'], vals['state'])
                    ),
                    'details': {'from': old.get('state'), 'to': vals['state']}
                })

            # Priority changed
            if 'priority' in vals and old.get('priority') != vals['priority']:
                case.timeline_ids.create({
                    'case_id': case.id,
                    'event_type': 'priority_changed',
                    'description': _('Priority changed from %s to %s') % (
                        dict(case._fields['priority'].selection).get(old.get('priority'), old.get('priority')),
                        dict(case._fields['priority'].selection).get(vals['priority'], vals['priority'])
                    ),
                    'details': {'from': old.get('priority'), 'to': vals['priority']}
                })

            # Assignment changed
            if 'assigned_to' in vals and old.get('assigned_to') != vals['assigned_to']:
                new_user = self.env['res.users'].browse(vals['assigned_to']) if vals['assigned_to'] else False
                old_user = self.env['res.users'].browse(old.get('assigned_to')) if old.get('assigned_to') else False
                case.timeline_ids.create({
                    'case_id': case.id,
                    'event_type': 'assigned',
                    'description': _('Case assigned from %s to %s') % (
                        old_user.name if old_user else 'Unassigned',
                        new_user.name if new_user else 'Unassigned'
                    ),
                    'details': {'from_user_id': old.get('assigned_to'), 'to_user_id': vals['assigned_to']}
                })

        # If state changed on screening cases, recalculate risk
        if 'state' in vals:
            screening_cases = self.filtered(lambda c: c.case_type == 'screening' and c.partner_id)
            for case in screening_cases:
                case.partner_id._compute_risk()
                _logger.info('Risk recalculated for partner %s after case %s state change',
                           case.partner_id.name, case.name)

        return result

    @api.depends('alert_ids')
    def _compute_alert_count(self):
        """Count related alerts."""
        for case in self:
            case.alert_count = len(case.alert_ids)

    @api.depends('move_ids')
    def _compute_move_count(self):
        """Count related transactions."""
        for case in self:
            case.move_count = len(case.move_ids)

    @api.depends('decision_ids')
    def _compute_decision_count(self):
        """Count decisions."""
        for case in self:
            case.decision_count = len(case.decision_ids)

    @api.depends('timeline_ids')
    def _compute_timeline_count(self):
        """Count timeline events."""
        for case in self:
            case.timeline_count = len(case.timeline_ids)

    @api.depends('note_ids')
    def _compute_note_count(self):
        """Count notes."""
        for case in self:
            case.note_count = len(case.note_ids)

    @api.depends('task_ids')
    def _compute_task_count(self):
        """Count tasks."""
        for case in self:
            case.task_count = len(case.task_ids)

    @api.depends('opened_date', 'priority', 'case_type')
    def _compute_sla_due_date(self):
        """Compute SLA due date based on priority and case type."""
        for case in self:
            if not case.opened_date:
                case.sla_due_date = False
                continue

            # SLA days based on priority
            sla_days = {
                'critical': 1,
                'high': 3,
                'medium': 7,
                'low': 14
            }.get(case.priority, 7)

            # Screening cases have tighter SLAs
            if case.case_type == 'screening':
                sla_days = max(1, sla_days // 2)

            case.sla_due_date = case.opened_date + timedelta(days=sla_days)

    @api.depends('sla_due_date', 'state')
    def _compute_overdue(self):
        """Compute if case is overdue."""
        now = fields.Datetime.now()
        for case in self:
            if case.state in ['closed', 'resolved_approved', 'resolved_rejected']:
                case.is_overdue = False
                case.days_overdue = 0
            elif case.sla_due_date:
                case.is_overdue = now > case.sla_due_date
                if case.is_overdue:
                    delta = now - case.sla_due_date
                    case.days_overdue = delta.days
                else:
                    case.days_overdue = 0
            else:
                case.is_overdue = False
                case.days_overdue = 0

    @api.constrains('state', 'decision_ids')
    def _check_state_transition(self):
        """Validate state transitions."""
        for case in self:
            # Can't resolve without a decision
            if case.state in ['resolved_approved', 'resolved_rejected'] and not case.decision_ids:
                raise models.ValidationError(
                    _('Cannot resolve case without making a decision. Please add a decision first.')
                )

            # Can't close screening case with true positive without ongoing tasks
            if case.state == 'closed' and case.case_type == 'screening':
                if case.decision_ids:
                    latest_decision = case.decision_ids.sorted('decided_date', reverse=True)[0]
                    if latest_decision.outcome == 'true_positive':
                        active_tasks = case.task_ids.filtered(lambda t: t.state != 'completed')
                        if not active_tasks:
                            _logger.warning(
                                'Closing screening case %s with true positive but no active monitoring tasks',
                                case.name
                            )

    def action_investigate(self):
        """Move case to investigating state."""
        self.write({'state': 'investigating'})
        self.message_post(
            body=_('Case moved to investigating by %s') % self.env.user.name,
            subject=_('Investigation Started')
        )

    def action_review(self):
        """Move case to review state."""
        self.write({'state': 'under_review'})
        self.message_post(
            body=_('Case moved to review by %s') % self.env.user.name,
            subject=_('Review Started')
        )

    def action_resolve(self):
        """Move case to resolved state."""
        self.write({'state': 'resolved_approved'})
        self.message_post(
            body=_('Case resolved by %s') % self.env.user.name,
            subject=_('Case Resolved')
        )

    def action_close(self):
        """Close the case."""
        self.write({
            'state': 'closed',
            'closed_date': fields.Datetime.now(),
        })
        self.message_post(
            body=_('Case closed by %s') % self.env.user.name,
            subject=_('Case Closed')
        )

        # Trigger risk recalculation for screening cases
        if self.case_type == 'screening' and self.partner_id:
            self.partner_id._compute_risk()
            _logger.info('Risk recalculated for partner %s after case %s closed',
                        self.partner_id.name, self.name)

    @api.model
    def cron_check_sla_violations(self):
        """Cron job to check for SLA violations and auto-escalate."""
        # Find all active cases
        active_cases = self.search([
            ('state', 'not in', ['closed', 'resolved_approved', 'resolved_rejected']),
            ('priority', '!=', 'critical')  # Don't escalate critical further
        ])

        # Filter overdue cases (computed field not searchable)
        overdue_cases = active_cases.filtered(lambda c: c.is_overdue)

        _logger.info('SLA check found %d overdue cases out of %d active cases',
                    len(overdue_cases), len(active_cases))

        for case in overdue_cases:
            # Check if already escalated recently (within last 3 days)
            recent_escalations = self.env['aml.case.timeline'].search([
                ('case_id', '=', case.id),
                ('event_type', '=', 'priority_changed'),
                ('event_date', '>=', fields.Datetime.now() - timedelta(days=3))
            ])

            if recent_escalations:
                continue

            # Auto-escalate priority
            old_priority = case.priority
            new_priority = {
                'low': 'medium',
                'medium': 'high',
                'high': 'critical'
            }.get(old_priority, 'high')

            case.write({'priority': new_priority})

            # Create timeline event
            case.timeline_ids.create({
                'case_id': case.id,
                'event_type': 'priority_changed',
                'description': _('Case auto-escalated from %s to %s due to SLA violation (%d days overdue)') % (
                    old_priority.title(),
                    new_priority.title(),
                    case.days_overdue
                ),
                'details': {
                    'from': old_priority,
                    'to': new_priority,
                    'reason': 'sla_violation',
                    'days_overdue': case.days_overdue
                }
            })

            # Notify assigned user
            if case.assigned_to:
                case.message_post(
                    body=_('Case is %d days overdue. Priority auto-escalated to %s. Please address urgently.') % (
                        case.days_overdue,
                        new_priority.title()
                    ),
                    subject=_('SLA Violation - Case Escalated'),
                    partner_ids=[case.assigned_to.partner_id.id],
                    message_type='notification',
                )

            _logger.info('Case %s auto-escalated from %s to %s (%d days overdue)',
                       case.name, old_priority, new_priority, case.days_overdue)

    def action_view_alerts(self):
        """View related alerts."""
        self.ensure_one()
        return {
            'name': _('Related Alerts'),
            'type': 'ir.actions.act_window',
            'res_model': 'aml.alert',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.alert_ids.ids)],
            'context': {'default_case_id': self.id},
        }

    def action_view_transactions(self):
        """View related transactions."""
        self.ensure_one()
        return {
            'name': _('Related Transactions'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.move_ids.ids)],
        }

    @api.model
    def _group_expand_state(self, states, domain):
        """Always show all state columns in kanban."""
        return ['open', 'investigating', 'under_review', 'pending_info',
                'resolved_approved', 'resolved_rejected', 'closed']
