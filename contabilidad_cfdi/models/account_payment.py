# -*- coding: utf-8 -*-

from odoo import models, fields, api 

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    diot = fields.Boolean('DIOT', default = False)
    diot_no_acreditable = fields.Boolean('No acreditable', default = False)

    @api.model
    def create(self, vals):
        res = super(AccountPayment, self).create(vals)
        if res.payment_type == 'outbound':
           res.diot = True
        return res
