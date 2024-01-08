from . import models
from odoo import SUPERUSER_ID
from odoo.api import Environment

def _post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    recs = env["crossovered.budget.lines"].search([])
    for rec in recs:
        purchase_order_line_ids = env["purchase.order.line"].search(
            [
                ("account_analytic_id", "=", rec.analytic_account_id.id),
                ("order_id.state", "=", "purchase"),
                ("order_id.date_approve", ">=", rec.date_from),
                ("order_id.date_approve", "<=", rec.date_to),
                ("order_id.invoice_status", "=", "to invoice"),
            ]
        )

        rec.write({"purchase_order_line_ids": [(4, line.id) for line in purchase_order_line_ids]})
