# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    def do_produce(self):
        for produce in self:
            produce.production_id.write({
                'as_lot': produce.finished_lot_id.id
            })
            for produce in produce.production_id.move_raw_ids:
                for move in self.raw_workorder_line_ids:
                    if produce.product_id == move.product_id:
                        produce.write({
                            'as_lotes' : move.lot_id.name
                        })
        return super(MrpProductProduce, self).do_produce()
        

    # def action_generate_serial(self):
    #     self.ensure_one()
    #     product_produce_wiz = self.env.ref('mrp.view_mrp_product_produce_wizard', False)
    #     self.finished_lot_id = self.env['stock.production.lot'].create({
    #         'product_id': self.product_id.id,
    #         'company_id': self.production_id.company_id.id
    #     })
    #     name = str(self.production_id.product_id.categ_id.as_code_orden)
    #     machine = self.production_id.as_machine_id.as_numero  
    #     if not machine:
    #         machine = 'ND'
    #     tipo_material = self.finished_lot_id.name
    #     new_name = name+'-'+machine+'-'+tipo_material
    #     self.finished_lot_id.write({
    #         'name': new_name
    #     })
    #     return {
    #         'name': _('Produce'),
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'mrp.product.produce',
    #         'res_id': self.id,
    #         'view_id': product_produce_wiz.id,
    #         'target': 'new',
    #     }