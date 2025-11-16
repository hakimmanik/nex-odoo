# -*- coding: utf-8 -*-
# Part of NexAML. See LICENSE file for full copyright and licensing details.

{
    'name': 'NexAML',
    'version': '19.0.1.0.0',
    'category': 'Compliance',
    'summary': 'Anti-Money Laundering (AML) Compliance for Odoo',
    'description': """
NexAML - AML Compliance Module
===============================
Comprehensive AML compliance solution including:
- Customer Risk Assessment (CRA)
- Sanctions Screening with OpenSanctions/Yente API
- Transaction Monitoring
- Case Management
- Alert Management
- SAR/STR Reporting
    """,
    'author': 'NexAML',
    'website': 'https://nexaml.com',
    'depends': [
        'base',
        'account',
        'mail',
        'contacts',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequences.xml',
        'data/cron.xml',
        'data/transaction_rules.xml',
        'views/menu.xml',
        'views/screening_views.xml',
        'views/case_management_views.xml',
        'views/transaction_monitoring_views.xml',
        'views/ewra_views.xml',
        'views/cra_views.xml',
        'views/res_partner_views.xml',
        'views/account_payment_method_views.xml',
        'views/pdf_report_actions.xml',
        # 'views/dashboard_views.xml',  # TODO: Fix circular XML references
        'views/report_wizard_views.xml',
        'wizards/ewra_wizard_views.xml',
        'reports/report_templates.xml',
        'reports/report_templates_extended.xml',
        'reports/report_templates_extended2.xml',
        'reports/ewra_report_comprehensive.xml',
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
