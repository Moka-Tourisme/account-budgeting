# Part of Odoo. See LICENSE file for full copyright and licensing details.
from . import models
from odoo import SUPERUSER_ID
from odoo.api import Environment


def _post_load_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    recs = env["crossovered.budget.lines"].search([])
    for rec in recs:
        invoice_line_ids = env["account.move.line"].search(
            [
                ("account_analytic_id", "=", rec.analytic_account_id.id),
                ("move_id.state", "=", "posted"),
                ("move_id.invoice_date", ">=", rec.date_from),
                ("move_id.invoice_date", "<=", rec.date_to),
                ("move_id.type", "=", "in_invoice"),
            ]
        )

        rec.write({"invoice_line_ids": [(4, line.id) for line in invoice_line_ids]})
