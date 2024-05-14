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
        compute="_compute_purchase_order_line_ids",
        string="Purchase Order Lines",
    )

    purchase_order_line_count = fields.Integer(
        compute="_compute_purchase_order_line_count",
        string="Purchase Order Lines",
    )

    @api.depends(
        "date_from", "date_to", "analytic_account_id", "purchase_order_line_ids.remaining_price_subtotal",
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
                            ('order_id.date_approve', '<=', date_to), ('order_id.invoice_status', '!=', 'invoiced')],
                    fields=['remaining_price_subtotal'],
                    groupby=['account_analytic_id'],
                    lazy=False
                )
                print("data: ", data)
                if data:
                    result = data[0]['remaining_price_subtotal']
            line.committed_amount = -result

    def _compute_purchase_order_line_ids(self):
        for line in self:
            purchase_line_ids = []
            date_to = line.date_to
            date_from = line.date_from
            if line.analytic_account_id.id:
                purchase_line_ids = self.env['purchase.order.line'].search(
                    [('account_analytic_id', '=', line.analytic_account_id.id),
                     ('order_id.state', '=', 'purchase'), ('order_id.date_approve', '>=', date_from),
                     ('order_id.date_approve', '<=', date_to)]
                )
                for purchase_line in purchase_line_ids:
                    if purchase_line.product_qty <= purchase_line.qty_invoiced:
                        purchase_line_ids -= purchase_line
            line.purchase_order_line_ids = purchase_line_ids

    @api.depends('purchase_order_line_ids')
    def _compute_purchase_order_line_count(self):
        for line in self:
            line.purchase_order_line_count = len(line.purchase_order_line_ids)

    def action_view_purchase_order_lines(self):
        action = self.env.ref('account_purchase_budget.action_purchase_order_line_tree').read()[0]
        action['domain'] = [('id', 'in', self.purchase_order_line_ids.ids)]
        return action

    def _compute_balance_amount(self):
        for line in self:
            line.balance_amount = line.planned_amount - (abs(line.practical_amount) + (abs(line.committed_amount)))
