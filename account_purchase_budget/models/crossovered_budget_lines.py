# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    committed_amount = fields.Float(
        compute="_compute_committed_amount",
        string="Committed Amount",
        digits=0,
        store=True,
    )

    purchase_order_line_ids = fields.One2many(
        comodel_name="purchase.order.line",
        inverse_name="crossovered_budget_line_id",
        string="Purchase Order Lines",
        store=True,
    )

    purchase_order_line_count = fields.Integer(
        compute="_compute_purchase_order_line_count",
        string="Purchase Order Lines",
    )

    @api.depends(
        "date_from", "date_to", "analytic_account_id", "purchase_order_line_ids.price_subtotal",
        "purchase_order_line_ids.order_id.state", "purchase_order_line_ids.order_id.invoice_status"
    )
    def _compute_committed_amount(self):
        for line in self:
            result = 0.0
            date_to = line.date_to
            date_from = line.date_from
            if line.analytic_account_id.id:
                data = self.env['purchase.order.line'].read_group(
                    domain=[('account_analytic_id', '=', line.analytic_account_id.id),
                            ('order_id.state', '=', 'purchase'), ('order_id.date_approve', '>=', date_from),
                            ('order_id.date_approve', '<=', date_to), ('order_id.state', '=', 'purchase')],
                    fields=['price_subtotal'],
                    groupby=['account_analytic_id'],
                    lazy=False
                )
                print("data: ", data)
                if data:
                    result = data[0]['price_subtotal']
            line.committed_amount = result

    @api.depends('purchase_order_line_ids')
    def _compute_purchase_order_line_count(self):
        for line in self:
            line.purchase_order_line_count = len(line.purchase_order_line_ids)

    def action_view_purchase_order_lines(self):
        action = self.env.ref('purchase.purchase_form_action').read()[0]
        action['domain'] = [('id', 'in', self.purchase_order_line_ids.order_id.ids)]
        action['context'] = {'create': False}
        return action

    @api.model
    def _action_update_budget_purchase_lines(self):
        print("PASSAGE ICI action_update_budget_purchase_lines")
        recs = self.env["crossovered.budget.lines"].search([])
        for rec in recs:
            purchase_order_line_ids = self.env["purchase.order.line"].search(
                [
                    ("account_analytic_id", "=", rec.analytic_account_id.id),
                    ("order_id.state", "=", "purchase"),
                    ("order_id.date_approve", ">=", rec.date_from),
                    ("order_id.date_approve", "<=", rec.date_to),
                ]
            )

            rec.write({"purchase_order_line_ids": [(4, line.id) for line in purchase_order_line_ids]})