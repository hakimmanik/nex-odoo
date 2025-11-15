# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Alert(models.Model):
    """Transaction monitoring alerts."""
    _name = 'aml.alert'
    _description = 'Alert'
    _order = 'alert_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Alert Reference',
        compute='_compute_name',
        store=True,
        help='Alert identifier'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        ondelete='cascade',
        help='Customer related to this alert'
    )
    move_id = fields.Many2one(
        'account.move',
        string='Transaction',
        ondelete='cascade',
        help='Transaction that triggered this alert'
    )
    rule_id = fields.Many2one(
        'aml.transaction.rule',
        string='Triggered Rule',
        required=True,
        ondelete='restrict',
        help='Rule that generated this alert'
    )
    alert_date = fields.Datetime(
        string='Alert Date',
        required=True,
        default=fields.Datetime.now,
        help='When the alert was generated'
    )
    severity = fields.Selection(
        [('low', 'Low'),
         ('medium', 'Medium'),
         ('high', 'High'),
         ('critical', 'Critical')],
        string='Severity',
        required=True,
        default='medium',
        tracking=True,
        help='Alert severity level'
    )
    status = fields.Selection(
        [('generated', 'Generated'),
         ('assigned', 'Assigned'),
         ('under_review', 'Under Review'),
         ('escalated', 'Escalated'),
         ('resolved_cleared', 'Resolved - Cleared'),
         ('resolved_true_positive', 'Resolved - True Positive'),
         ('resolved_false_positive', 'Resolved - False Positive')],
        string='Status',
        required=True,
        default='generated',
        tracking=True,
        group_expand='_group_expand_status',
        help='Current status of the alert'
    )
    case_id = fields.Many2one(
        'aml.case',
        string='Related Case',
        help='Case this alert was escalated to'
    )

    # Alert Details
    triggered_value = fields.Float(
        string='Triggered Value',
        help='Value that triggered the alert'
    )
    alert_reason = fields.Text(
        string='Reason',
        required=True,
        help='Why this alert was triggered'
    )
    alert_details = fields.Text(
        string='Details',
        help='Additional details about the alert'
    )

    # Review Information
    review_notes = fields.Text(
        string='Review Notes',
        tracking=True,
        help='Notes from reviewing this alert'
    )
    reviewed_by = fields.Many2one(
        'res.users',
        string='Reviewed By',
        help='User who reviewed/closed this alert'
    )
    reviewed_date = fields.Datetime(
        string='Reviewed Date',
        help='When the alert was reviewed'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        help='Company'
    )

    @api.depends('partner_id', 'rule_id', 'alert_date')
    def _compute_name(self):
        """Generate alert reference."""
        for alert in self:
            if alert.partner_id and alert.rule_id:
                date_str = fields.Datetime.to_string(alert.alert_date)[:10]
                alert.name = f"ALT-{alert.id or 'NEW'}: {alert.rule_id.code} - {alert.partner_id.name}"
            else:
                alert.name = 'New Alert'

    def action_assign(self):
        """Assign alert to current user."""
        self.write({
            'status': 'assigned',
            'reviewed_by': self.env.user.id,
        })
        self.message_post(
            body=_('Alert assigned to %s') % self.env.user.name,
            subject=_('Alert Assigned')
        )

    def action_start_review(self):
        """Start reviewing the alert."""
        self.write({
            'status': 'under_review',
            'reviewed_by': self.env.user.id,
            'reviewed_date': fields.Datetime.now(),
        })
        self.message_post(
            body=_('Review started by %s') % self.env.user.name,
            subject=_('Review Started')
        )

    def action_resolve_cleared(self):
        """Resolve alert as cleared (false positive)."""
        self.write({
            'status': 'resolved_cleared',
            'reviewed_by': self.env.user.id,
            'reviewed_date': fields.Datetime.now(),
        })
        self.message_post(
            body=_('Alert resolved as cleared by %s') % self.env.user.name,
            subject=_('Alert Cleared')
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Alert resolved as cleared'),
                'type': 'success',
            }
        }

    def action_resolve_true_positive(self):
        """Resolve alert as true positive."""
        self.write({
            'status': 'resolved_true_positive',
            'reviewed_by': self.env.user.id,
            'reviewed_date': fields.Datetime.now(),
        })
        self.message_post(
            body=_('Alert resolved as true positive by %s') % self.env.user.name,
            subject=_('True Positive Confirmed')
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Alert resolved as true positive'),
                'type': 'warning',
            }
        }

    def action_resolve_false_positive(self):
        """Resolve alert as false positive."""
        self.write({
            'status': 'resolved_false_positive',
            'reviewed_by': self.env.user.id,
            'reviewed_date': fields.Datetime.now(),
        })
        self.message_post(
            body=_('Alert resolved as false positive by %s') % self.env.user.name,
            subject=_('False Positive')
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Alert closed'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_escalate_to_case(self):
        """Escalate alert to a case for investigation."""
        self.ensure_one()

        # Create case
        case_vals = {
            'partner_id': self.partner_id.id,
            'case_type': 'transaction',
            'priority': 'high' if self.severity in ('high', 'critical') else 'medium',
            'description': self.alert_reason,
            'alert_ids': [(6, 0, [self.id])],
        }

        if self.move_id:
            case_vals['move_ids'] = [(6, 0, [self.move_id.id])]

        case = self.env['aml.case'].create(case_vals)

        # Update alert status
        self.write({
            'status': 'escalated',
            'case_id': case.id,
            'reviewed_by': self.env.user.id,
            'reviewed_date': fields.Datetime.now(),
        })

        self.message_post(
            body=_('Escalated to case %s by %s') % (case.name, self.env.user.name),
            subject=_('Escalated to Case')
        )

        return {
            'type': 'ir.actions.act_window',
            'name': _('Case'),
            'res_model': 'aml.case',
            'res_id': case.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def _group_expand_status(self, states, domain):
        """Always show all status columns in kanban."""
        return ['generated', 'assigned', 'under_review', 'escalated',
                'resolved_cleared', 'resolved_true_positive', 'resolved_false_positive']
