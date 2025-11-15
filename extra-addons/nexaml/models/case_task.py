# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class CaseTask(models.Model):
    """Case investigation tasks."""
    _name = 'aml.case.task'
    _description = 'Case Task'
    _order = 'due_date asc, priority desc, id desc'

    case_id = fields.Many2one(
        'aml.case',
        string='Case',
        required=True,
        ondelete='cascade',
        help='Related case'
    )
    name = fields.Char(
        string='Task',
        required=True,
        help='Task description'
    )
    task_type = fields.Selection(
        [('document_review', 'Document Review'),
         ('customer_contact', 'Contact Customer'),
         ('data_collection', 'Data Collection'),
         ('risk_analysis', 'Risk Analysis'),
         ('approval_required', 'Approval Required'),
         ('reporting', 'Reporting'),
         ('other', 'Other')],
        string='Task Type',
        default='other',
        help='Type of task'
    )
    state = fields.Selection(
        [('pending', 'Pending'),
         ('in_progress', 'In Progress'),
         ('completed', 'Completed'),
         ('cancelled', 'Cancelled')],
        string='State',
        default='pending',
        required=True,
        help='Task status'
    )
    priority = fields.Selection(
        [('low', 'Low'),
         ('medium', 'Medium'),
         ('high', 'High')],
        string='Priority',
        default='medium',
        help='Task priority'
    )
    assigned_to = fields.Many2one(
        'res.users',
        string='Assigned To',
        help='User responsible for this task'
    )
    due_date = fields.Date(
        string='Due Date',
        help='Task due date'
    )
    completed_date = fields.Datetime(
        string='Completed Date',
        readonly=True,
        help='When the task was completed'
    )
    notes = fields.Text(
        string='Notes',
        help='Task notes'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        help='Company'
    )

    def action_mark_done(self):
        """Mark task as completed."""
        self.write({
            'state': 'completed',
            'completed_date': fields.Datetime.now()
        })
        # Log timeline event
        for task in self:
            task.case_id.timeline_ids.create({
                'case_id': task.case_id.id,
                'event_type': 'task_completed',
                'description': _('Task completed: %s') % task.name,
                'details': {'task_id': task.id, 'task_type': task.task_type}
            })

    def action_mark_in_progress(self):
        """Mark task as in progress."""
        self.write({'state': 'in_progress'})
