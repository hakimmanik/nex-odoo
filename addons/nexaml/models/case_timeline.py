# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import json
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class CaseTimeline(models.Model):
    """Case timeline event tracking."""
    _name = 'aml.case.timeline'
    _description = 'Case Timeline Event'
    _order = 'event_date desc, id desc'

    case_id = fields.Many2one(
        'aml.case',
        string='Case',
        required=True,
        ondelete='cascade',
        help='Related case'
    )
    event_type = fields.Selection(
        [('status_changed', 'Status Changed'),
         ('priority_changed', 'Priority Changed'),
         ('assigned', 'Case Assigned'),
         ('decision_made', 'Decision Made'),
         ('note_added', 'Note Added'),
         ('task_completed', 'Task Completed'),
         ('attachment_added', 'Attachment Added'),
         ('alert_linked', 'Alert Linked'),
         ('transaction_linked', 'Transaction Linked'),
         ('other', 'Other')],
        string='Event Type',
        required=True,
        help='Type of timeline event'
    )
    description = fields.Text(
        string='Description',
        required=True,
        help='Description of the event'
    )
    details = fields.Json(
        string='Details',
        help='Additional structured details (JSON)'
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        help='User who triggered the event'
    )
    event_date = fields.Datetime(
        string='Event Date',
        required=True,
        default=fields.Datetime.now,
        help='When the event occurred'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        help='Company'
    )

    def _format_details(self):
        """Format details JSON for display."""
        self.ensure_one()
        if not self.details:
            return ''
        try:
            return json.dumps(self.details, indent=2)
        except:
            return str(self.details)
