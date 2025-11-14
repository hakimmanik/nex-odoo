# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Screening(models.Model):
    """Sanctions and PEP screening results."""
    _name = 'aml.screening'
    _description = 'Screening Result'
    _order = 'screening_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Reference',
        compute='_compute_name',
        store=True,
        help='Screening reference identifier'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        ondelete='cascade',
        help='Customer being screened'
    )
    screening_type = fields.Selection(
        [('sanctions', 'Sanctions'),
         ('pep', 'PEP'),
         ('adverse_media', 'Adverse Media')],
        string='Screening Type',
        required=True,
        default='sanctions',
        help='Type of screening performed'
    )
    screening_date = fields.Datetime(
        string='Screening Date',
        required=True,
        default=fields.Datetime.now,
        help='When screening was performed'
    )
    status = fields.Selection(
        [('pending', 'Pending'),
         ('clear', 'Clear'),
         ('match', 'Match Found'),
         ('false_positive', 'False Positive')],
        string='Status',
        required=True,
        default='pending',
        tracking=True,
        help='Screening result status'
    )
    match_score = fields.Float(
        string='Match Score',
        help='Confidence score of the match (0-100)'
    )
    matched_name = fields.Char(
        string='Matched Name',
        help='Name from sanctions/PEP list that matched'
    )
    matched_entity_id = fields.Char(
        string='Entity ID',
        help='External ID of matched entity from screening service'
    )
    matched_countries = fields.Char(
        string='Countries',
        help='Countries associated with matched entity'
    )
    matched_datasets = fields.Char(
        string='Datasets',
        help='Sanctions lists/datasets where match was found'
    )
    screening_data = fields.Text(
        string='Raw Screening Data',
        help='Full JSON response from screening API'
    )

    # Review fields
    reviewed_by = fields.Many2one(
        'res.users',
        string='Reviewed By',
        help='User who reviewed the screening result'
    )
    review_date = fields.Datetime(
        string='Review Date',
        help='When the result was reviewed'
    )
    review_notes = fields.Text(
        string='Review Notes',
        help='Notes from reviewing the screening result'
    )

    @api.depends('partner_id', 'screening_type', 'screening_date')
    def _compute_name(self):
        """Generate screening reference."""
        for screening in self:
            if screening.partner_id and screening.screening_type:
                date_str = fields.Datetime.to_string(screening.screening_date)[:10]
                screening.name = f"{screening.partner_id.name} - {screening.screening_type} - {date_str}"
            else:
                screening.name = 'New Screening'

    def action_mark_false_positive(self):
        """Mark screening result as false positive."""
        self.ensure_one()
        self.write({
            'status': 'false_positive',
            'reviewed_by': self.env.user.id,
            'review_date': fields.Datetime.now(),
        })
        self.message_post(
            body=_('Marked as false positive by %s') % self.env.user.name,
            subject=_('False Positive')
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Screening result marked as false positive'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_review(self):
        """Open review wizard or mark as reviewed."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Review Screening'),
            'res_model': 'aml.screening',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
