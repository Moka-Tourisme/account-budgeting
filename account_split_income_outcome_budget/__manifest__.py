# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Budgets Management Income/Outcome",
    "version": "15.0.1.0.0",
    "category": "Accounting",
    "license": "LGPL-3",
    "author": "Odoo S.A., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-budgeting",
    "depends": ["account_budget_oca", "sale"],
    'auto_install': False,
    "data": [
        "views/crossovered_budget_lines.xml",
        "views/account_budget_views.xml",
    ],
}
