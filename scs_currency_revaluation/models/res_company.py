# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    unrealised_inc_curr_account_id = fields.Many2one(
        'account.account', string="Gain Exchange Rate Account",
        domain="[('type', '=', 'other')]")
    unrealised_exp_curr_account_id = fields.Many2one(
        'account.account', string="Loss Exchange Rate Account",
        domain="[('type', '=', 'other')]")
