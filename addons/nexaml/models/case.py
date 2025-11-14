# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

import logging

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

    # Investigation Details
    description = fields.Text(
        string='Description',
        help='Initial description of the case'
    )
    investigation_notes = fields.Html(
        string='Investigation Notes',
        help='Detailed notes from investigation'
    )

    # Decision (dynamic based on case type)
    decision = fields.Selection(
        selection='_get_decision_selection',
        string='Decision',
        tracking=True,
        help='Decision made after investigation'
    )

    # Action Taken (dynamic based on decision)
    action_taken = fields.Selection(
        [('no_action', 'No Action Required'),
         ('customer_contacted', 'Customer Contacted'),
         ('enhanced_due_diligence', 'Enhanced Due Diligence'),
         ('sar_filed', 'SAR Filed'),
         ('transaction_blocked', 'Transaction Blocked'),
         ('relationship_terminated', 'Relationship Terminated'),
         ('reported_to_authorities', 'Reported to Authorities'),
         ('ongoing_monitoring', 'Ongoing Monitoring'),
         ('other', 'Other')],
        string='Action Taken',
        tracking=True,
        help='Action taken based on the decision'
    )

    resolution_notes = fields.Text(
        string='Resolution Notes',
        tracking=True,
        help='Notes about the resolution'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        help='Company'
    )

    @api.model
    def _get_decision_selection(self):
        """Return decision options based on case type."""
        # Get case_type from context or self
        case_type = self._context.get('default_case_type') or (self.case_type if self else False)

        if case_type == 'screening':
            return [
                ('confirmed_match', 'Confirmed Match'),
                ('potential_match', 'Potential Match'),
                ('false_positive', 'False Positive'),
            ]
        elif case_type == 'transaction':
            return [
                ('legitimate', 'Legitimate Transaction'),
                ('suspicious', 'Suspicious - Requires Monitoring'),
                ('escalate', 'Escalate to SAR'),
                ('false_positive', 'False Positive'),
            ]
        elif case_type == 'risk':
            return [
                ('risk_accepted', 'Risk Accepted'),
                ('risk_mitigated', 'Risk Mitigated'),
                ('risk_rejected', 'Risk Rejected - Terminate'),
            ]
        else:
            return [
                ('approved', 'Approved'),
                ('rejected', 'Rejected'),
                ('requires_further_review', 'Requires Further Review'),
            ]

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate case number."""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('aml.case') or _('New')
        return super(Case, self).create(vals_list)

    def write(self, vals):
        """Override write to trigger actions based on decision and recalculate risk."""
        result = super(Case, self).write(vals)

        # Handle decision changes and trigger appropriate actions
        if 'decision' in vals:
            for case in self:
                case._handle_decision_action()

        # If resolution or state changed on screening cases, recalculate risk
        if ('resolution' in vals or 'state' in vals or 'decision' in vals):
            screening_cases = self.filtered(lambda c: c.case_type == 'screening' and c.partner_id)
            for case in screening_cases:
                case.partner_id._compute_risk()
                _logger.info('Risk recalculated for partner %s after case %s resolution change',
                           case.partner_id.name, case.name)

        return result

    def _handle_decision_action(self):
        """Handle actions based on decision for screening cases."""
        self.ensure_one()

        if self.case_type != 'screening':
            return

        # Update partner sanctions status based on decision
        if self.decision == 'confirmed_match':
            # Set sanctions_status to 'match'
            self.partner_id.sanctions_status = 'match'
            self.partner_id.message_post(
                body=_('Screening case %s: Confirmed Match. Enhanced monitoring required.') % self.name,
                subject=_('Confirmed Sanctions Match'),
                message_type='notification',
            )
            _logger.info('Partner %s sanctions status set to "match" (confirmed)', self.partner_id.name)
        elif self.decision == 'potential_match':
            # Set as match since ongoing monitoring required
            self.partner_id.sanctions_status = 'match'
            self.partner_id.message_post(
                body=_('Screening case %s: Potential Match. Ongoing monitoring required.') % self.name,
                subject=_('Potential Sanctions Match'),
                message_type='notification',
            )
            _logger.info('Partner %s sanctions status set to "match" (potential)', self.partner_id.name)
        elif self.decision == 'false_positive':
            # Check if all screening cases are resolved as false positive
            other_cases = self.env['aml.case'].search([
                ('partner_id', '=', self.partner_id.id),
                ('case_type', '=', 'screening'),
                ('id', '!=', self.id)
            ])

            # Check if any other cases are not false positive or still open
            has_active_concerns = any(
                case.state in ['open', 'investigating', 'under_review', 'pending_info'] or
                (case.state in ['resolved_approved', 'resolved_rejected', 'closed'] and
                 case.decision in ['confirmed_match', 'potential_match'])
                for case in other_cases
            )

            if not has_active_concerns:
                # No other open or confirmed cases, clear sanctions status
                self.partner_id.sanctions_status = 'clear'
                self.partner_id.message_post(
                    body=_('Screening case %s: False Positive. Sanctions status cleared.') % self.name,
                    subject=_('False Positive - Cleared'),
                    message_type='notification',
                )
                _logger.info('Partner %s sanctions status cleared (false positive case %s)',
                           self.partner_id.name, self.name)
            else:
                # Other cases still have concerns, keep as match
                self.partner_id.message_post(
                    body=_('Screening case %s: False Positive. Status remains "match" due to other active cases.') % self.name,
                    subject=_('False Positive'),
                    message_type='notification',
                )
                _logger.info('Partner %s sanctions status remains "match" due to other cases', self.partner_id.name)

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
