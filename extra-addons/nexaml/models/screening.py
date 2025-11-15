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
    fingerprint = fields.Char(
        string='Fingerprint',
        compute='_compute_fingerprint',
        store=True,
        index=True,
        help='Unique fingerprint for deduplication based on matched entity'
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

    @api.depends('screening_type', 'matched_entity_id', 'matched_name', 'match_score')
    def _compute_fingerprint(self):
        """Compute unique fingerprint for deduplication."""
        for screening in self:
            screening.fingerprint = screening._generate_fingerprint()

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to auto-create cases for matches."""
        screenings = super(Screening, self).create(vals_list)
        for screening in screenings:
            # Force compute fingerprint
            screening.fingerprint = screening._generate_fingerprint()
            # Auto-create case if match found
            if screening.status == 'match' and screening.match_score:
                screening._create_case_from_match()
        return screenings

    def write(self, vals):
        """Override write to handle status changes."""
        result = super(Screening, self).write(vals)

        # If status changed to 'match', create case
        if vals.get('status') == 'match':
            for screening in self:
                if not screening._has_active_case():
                    screening._create_case_from_match()

        return result

    def _generate_fingerprint(self):
        """Generate unique fingerprint for deduplication based on API result."""
        self.ensure_one()
        import hashlib
        import json

        # Use hash of screening_data (raw API result) for deduplication
        if self.screening_data:
            # Parse and normalize the JSON to ensure consistent hashing
            try:
                data = json.loads(self.screening_data) if isinstance(self.screening_data, str) else self.screening_data
                # Create stable JSON string (sorted keys)
                stable_json = json.dumps(data, sort_keys=True)
                # Hash it
                hash_obj = hashlib.sha256(stable_json.encode('utf-8'))
                fingerprint = hash_obj.hexdigest()[:32]  # Use first 32 chars of hash
            except:
                # Fallback to simple hash if JSON parsing fails
                fingerprint = hashlib.sha256(self.screening_data.encode('utf-8')).hexdigest()[:32]
        else:
            # Fallback to old method if no screening_data
            parts = [
                self.screening_type or '',
                self.matched_entity_id or '',
                self.matched_name or '',
                str(int(self.match_score)) if self.match_score else '0',
            ]
            fingerprint = '|'.join(parts)

        return fingerprint

    def _has_active_case(self):
        """Check if screening already has an active case (with deduplication)."""
        self.ensure_one()
        Case = self.env['aml.case']

        # Get current fingerprint
        current_fingerprint = self.fingerprint or self._generate_fingerprint()

        if not current_fingerprint:
            return False

        # Search for existing screenings with EXACT same fingerprint
        existing_screenings = self.search([
            ('id', '!=', self.id),
            ('partner_id', '=', self.partner_id.id),
            ('fingerprint', '=', current_fingerprint),
            ('status', '=', 'match'),
        ])

        # Check if any of those screenings have active cases
        for existing in existing_screenings:
            # Look for cases linked to this screening via timeline
            timeline_entries = self.env['aml.case.timeline'].search([
                ('details', 'ilike', f'"screening_id": {existing.id}'),
                ('event_type', '=', 'other')
            ])

            if timeline_entries:
                for timeline in timeline_entries:
                    # Check if case exists (even if closed)
                    if timeline.case_id:
                        # Log that we found a duplicate
                        if timeline.case_id.state not in ['closed', 'resolved_approved', 'resolved_rejected']:
                            # Active case - add note to it
                            self.env['aml.case.timeline'].create({
                                'case_id': timeline.case_id.id,
                                'event_type': 'note_added',
                                'description': f'Duplicate screening detected (ID: {self.id}), case not created',
                                'details': {
                                    'duplicate_screening_id': self.id,
                                    'original_screening_id': existing.id,
                                    'fingerprint': current_fingerprint,
                                }
                            })
                        else:
                            # Closed case - just log to partner
                            self.partner_id.message_post(
                                body=f'Duplicate screening detected. Previously investigated in case {timeline.case_id.name} (Status: {timeline.case_id.state}). No new case created.',
                                subject='Duplicate Screening',
                                message_type='notification',
                            )
                        return True

        return False

    def _create_case_from_match(self):
        """Create case when screening match is found."""
        self.ensure_one()

        # Skip if already has active case
        if self._has_active_case():
            return False

        Case = self.env['aml.case']

        # Build description
        description = f"Screening match found for {self.partner_id.name}\n"
        description += f"Type: {dict(self._fields['screening_type'].selection).get(self.screening_type)}\n"
        description += f"Match Score: {self.match_score}%\n"
        if self.matched_name:
            description += f"Matched Name: {self.matched_name}\n"
        if self.matched_datasets:
            description += f"Datasets: {self.matched_datasets}\n"
        if self.matched_countries:
            description += f"Countries: {self.matched_countries}\n"

        # Determine priority based on score
        if self.match_score >= 90:
            priority = 'critical'
        elif self.match_score >= 75:
            priority = 'high'
        elif self.match_score >= 60:
            priority = 'medium'
        else:
            priority = 'low'

        # Map screening type to case type
        case_type_map = {
            'sanctions': 'sanctions',
            'pep': 'pep',
            'adverse_media': 'adverse_media',
        }
        case_type = case_type_map.get(self.screening_type, 'other')

        # Create case
        case = Case.sudo().create({
            'partner_id': self.partner_id.id,
            'case_type': case_type,
            'priority': priority,
            'description': description,
            'state': 'open',
        })

        # Log timeline event with full screening data
        import json
        timeline_details = {
            'screening_id': self.id,
            'match_score': self.match_score,
            'matched_name': self.matched_name,
            'fingerprint': self.fingerprint,
        }

        # Attach raw screening data if available
        if self.screening_data:
            try:
                screening_data_obj = json.loads(self.screening_data) if isinstance(self.screening_data, str) else self.screening_data
                timeline_details['screening_api_result'] = screening_data_obj
            except:
                timeline_details['screening_api_result'] = self.screening_data

        case.timeline_ids.create({
            'case_id': case.id,
            'event_type': 'other',
            'description': f'Case created from {self.screening_type} screening match',
            'details': timeline_details
        })

        return case

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
