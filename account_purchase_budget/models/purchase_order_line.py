# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class PurchaseOrderLines(models.Model):
    _inherit = "purchase.order.line"

    crossovered_budget_line_id = fields.Many2one(
        comodel_name="crossovered.budget.lines", string="Budget Line"
    )

    def write(self, vals):
        res = super().write(vals)
        if vals.get('account_analytic_id'):
            # Search for budget with the same analytic account
            budget = self.env['crossovered.budget.lines'].search([('analytic_account_id', '=', vals.get('account_analytic_id'))])
            # Add the line to the budget
            budget.write({'purchase_order_line_ids': [(4, self.id)]})
        return res

    def create(self, vals):
        res = super().create(vals)
        for line in res:
            if line.account_analytic_id:
                budget = self.env['crossovered.budget.lines'].search([('analytic_account_id', '=', line.account_analytic_id.id)])
                budget.write({'purchase_order_line_ids': [(4, line.id)]})
        return res

