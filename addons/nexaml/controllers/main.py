# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request, route


class NexAMLController(http.Controller):
    """Custom URL routes for NexAML."""

    @route('/aml/dashboard', type='http', auth='user')
    def dashboard(self, **kw):
        """Dashboard view."""
        action = request.env.ref('nexaml.action_dashboard')
        menu = request.env.ref('nexaml.menu_dashboard')
        return request.redirect(f'/web#action={action.id}&menu_id={menu.id}')

    @route('/aml/cases', type='http', auth='user')
    def cases(self, **kw):
        """Cases list view."""
        action = request.env.ref('nexaml.action_case')
        menu = request.env.ref('nexaml.menu_cases')
        return request.redirect(f'/web#action={action.id}&menu_id={menu.id}')

    @route('/aml/alerts', type='http', auth='user')
    def alerts(self, **kw):
        """Alerts list view."""
        action = request.env.ref('nexaml.action_alert')
        menu = request.env.ref('nexaml.menu_alerts')
        return request.redirect(f'/web#action={action.id}&menu_id={menu.id}')

    @route('/aml/screenings', type='http', auth='user')
    def screenings(self, **kw):
        """Screenings list view."""
        action = request.env.ref('nexaml.action_screening')
        menu = request.env.ref('nexaml.menu_screenings')
        return request.redirect(f'/web#action={action.id}&menu_id={menu.id}')

    @route('/aml/rules', type='http', auth='user')
    def rules(self, **kw):
        """Transaction rules configuration."""
        action = request.env.ref('nexaml.action_transaction_rule')
        menu = request.env.ref('nexaml.menu_transaction_rules')
        return request.redirect(f'/web#action={action.id}&menu_id={menu.id}')

    @route('/aml/case/<int:case_id>', type='http', auth='user')
    def case_detail(self, case_id, **kw):
        """Individual case view."""
        case = request.env['aml.case'].browse(case_id)
        if not case.exists():
            return request.not_found()
        return request.redirect(f'/web#id={case_id}&model=aml.case&view_type=form')

    @route('/aml/alert/<int:alert_id>', type='http', auth='user')
    def alert_detail(self, alert_id, **kw):
        """Individual alert view."""
        alert = request.env['aml.alert'].browse(alert_id)
        if not alert.exists():
            return request.not_found()
        return request.redirect(f'/web#id={alert_id}&model=aml.alert&view_type=form')
