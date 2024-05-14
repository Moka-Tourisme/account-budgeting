# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    split_income = fields.Boolean(
        string="Allow To Split Income and Outcome in a budget",
        default=False,
    )

    income_amount = fields.Float(
        compute="_compute_income_amount",
        string="Income Amount",
        digits=0,
        store=True,
        precompute=True
    )

    income_invoice_line_ids = fields.One2many(
        comodel_name="account.move.line",
        compute="_compute_income_invoice_line_ids",
        string="Income Sale Order Lines",
    )

    income_invoice_line_count = fields.Integer(
        compute="_compute_income_invoice_line_count",
        string="Income Sale Order Lines",
    )

    @api.depends(
        "split_income", "general_budget_id.account_ids", "date_from", "date_to",
        "analytic_account_id", "analytic_account_id.line_ids"
    )
    def _compute_practical_amount(self):
        for line in self:
            if not line.split_income:
                super(CrossoveredBudgetLines, line)._compute_practical_amount()
            else:
                result = 0.0
                acc_ids = line.general_budget_id.account_ids.ids
                date_to = line.date_to
                date_from = line.date_from
                if line.analytic_account_id.id and acc_ids:
                    self.env.cr.execute(
                        """
                        SELECT SUM(amount)
                        FROM account_analytic_line
                        WHERE account_id=%s
                            AND (date between %s
                            AND %s)
                            AND general_account_id IN %s 
                            AND amount < 0""",
                        (line.analytic_account_id.id, date_from, date_to, tuple(acc_ids)),
                    )
                    result = self.env.cr.fetchone()[0] or 0.0
                    line.practical_amount = result
                else:
                    line.practical_amount = 0.0

    @api.depends("split_income")
    def _compute_invoice_line_ids(self):
        for line in self:
            if not line.split_income:
                super(CrossoveredBudgetLines, line)._compute_invoice_line_ids()
            else:
                invoice_line_ids = []
                acc_ids = line.general_budget_id.account_ids.ids
                date_to = line.date_to
                date_from = line.date_from
                if line.analytic_account_id.id and acc_ids:
                    self.env.cr.execute(
                        """
                        SELECT DISTINCT aml.move_id
                        FROM account_move_line as aml
                        INNER JOIN account_analytic_line as aal ON aal.move_id = aml.id 
                        WHERE aal.account_id=%s
                            AND (aal.date between %s
                            AND %s)
                            AND aal.general_account_id IN %s
                            AND aal.amount < 0""",
                        (line.analytic_account_id.id, date_from, date_to, tuple(acc_ids)),
                    )
                    move_ids = [move[0] for move in self.env.cr.fetchall() or []]
                    if move_ids:
                        invoice_line_ids = self.env['account.move.line'].search(
                            [
                                ('move_id', 'in', move_ids),
                                ('analytic_account_id', '=', line.analytic_account_id.id),
                                ('account_id', 'in', acc_ids),
                            ]
                        )
                    line.invoice_line_ids = invoice_line_ids
                else:
                    line.invoice_line_ids = []

    @api.depends(
        "split_income","general_budget_id.account_ids", "date_from", "date_to", "analytic_account_id", "analytic_account_id.line_ids"
    )
    def _compute_income_amount(self):
        for line in self:
            if not line.split_income:
                return 0.0
            result = 0.0
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = line.date_to
            date_from = line.date_from
            if line.analytic_account_id.id and acc_ids:
                self.env.cr.execute(
                    """
                    SELECT SUM(amount)
                    FROM account_analytic_line
                    WHERE account_id = %s
                    AND (date between %s and %s)
                    AND general_account_id in %s
                    AND amount > 0
                    """,
                    (line.analytic_account_id.id, date_from, date_to, tuple(acc_ids)),
                )
                result = self.env.cr.fetchone()[0] or 0.0
                line.income_amount = result
            else:
                line.income_amount = 0.0

    @api.depends("split_income")
    def _compute_income_invoice_line_ids(self):
        for line in self:
            invoice_line_ids = []
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = line.date_to
            date_from = line.date_from
            if line.analytic_account_id.id:
                self.env.cr.execute(
                    """
                    SELECT DISTINCT aml.move_id
                    FROM account_move_line as aml
                    INNER JOIN account_analytic_line as aal ON aal.move_id = aml.id 
                    WHERE aal.account_id=%s
                        AND (aal.date between %s
                        AND %s)
                        AND aal.general_account_id IN %s
                        AND aal.amount > 0""",
                    (line.analytic_account_id.id, date_from, date_to, tuple(acc_ids)),
                )
            move_ids = [move[0] for move in self.env.cr.fetchall()]
            invoice_line_ids = self.env['account.move.line'].search(
                [
                    ('move_id', 'in', move_ids),
                    ('analytic_account_id', '=', line.analytic_account_id.id),
                    ('account_id', 'in', acc_ids),
                ]
            )
            line.income_invoice_line_ids = invoice_line_ids

    @api.depends("income_invoice_line_ids")
    def _compute_income_invoice_line_count(self):
        for line in self:
            line.income_invoice_line_count = len(line.income_invoice_line_ids)

    def action_view_income_invoice_lines(self):
        action = self.env.ref('account_budget_oca.action_account_move_line_tree').read()[0]
        action['domain'] = [('id', 'in', self.income_invoice_line_ids.ids)]
        return action
