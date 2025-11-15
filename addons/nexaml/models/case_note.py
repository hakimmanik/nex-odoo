# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class CaseNote(models.Model):
    """Case investigation notes."""
    _name = 'aml.case.note'
    _description = 'Case Note'
    _order = 'created_date desc, id desc'

    case_id = fields.Many2one(
        'aml.case',
        string='Case',
        required=True,
        ondelete='cascade',
        help='Related case'
    )
    note_type = fields.Selection(
        [('investigation', 'Investigation Note'),
         ('customer_contact', 'Customer Contact'),
         ('internal_discussion', 'Internal Discussion'),
         ('external_inquiry', 'External Inquiry'),
         ('document_review', 'Document Review'),
         ('risk_analysis', 'Risk Analysis'),
         ('other', 'Other')],
        string='Note Type',
        default='investigation',
        required=True,
        help='Type of note'
    )
    title = fields.Char(
        string='Title',
        required=True,
        help='Note title/summary'
    )
    content = fields.Html(
        string='Content',
        required=True,
        help='Detailed note content'
    )
    is_confidential = fields.Boolean(
        string='Confidential',
        default=False,
        help='Mark as confidential (restricted access)'
    )
    author_id = fields.Many2one(
        'res.users',
        string='Author',
        required=True,
        default=lambda self: self.env.user,
        help='User who created the note'
    )
    created_date = fields.Datetime(
        string='Created Date',
        required=True,
        default=fields.Datetime.now,
        help='When the note was created'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        help='Company'
    )
