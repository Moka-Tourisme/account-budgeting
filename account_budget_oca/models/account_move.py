# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo import SUPERUSER_ID
from odoo.api import Environment

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    crossovered_budget_line_id = fields.Many2one(
        comodel_name="crossovered.budget.lines", string="Budget Line"
    )

    balance_credit_debit = fields.Monetary(
        compute="_compute_balance_credit_debit", string="Balance Credit Debit", store=True, precompute=True
    )

    @api.depends("debit", "credit")
    def _compute_balance_credit_debit(self):
        for line in self:
            line.balance_credit_debit = line.debit - line.credit

    def write(self, vals):
        res = super().write(vals)
        if vals.get('account_analytic_id'):
            # Search for budget with the same analytic account
            budget = self.env['crossovered.budget.lines'].search([('analytic_account_id', '=', vals.get('account_analytic_id'))])
            # Add the line to the budget
            budget.write({'invoice_line_ids': [(4, self.id)]})
        return res

    def create(self, vals):
        res = super().create(vals)
        for line in res:
            if line.analytic_account_id:
                budget = self.env['crossovered.budget.lines'].search([('analytic_account_id', '=', line.analytic_account_id.id)])
                budget.write({'invoice_line_ids': [(4, line.id)]})
        return res


