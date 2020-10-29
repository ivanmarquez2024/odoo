# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils, float_compare    
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError
import logging
from odoo.tests import Form
from odoo.exceptions import Warning, UserError, AccessError
_logger = logging.getLogger(__name__)

class as_mrp_workorder(models.Model):
    _inherit = "mrp.production"

class asMRPmove(models.Model):
    _inherit = 'stock.move'

    as_consumido = fields.Boolean(string='Consumido')

    def get_sentinel_close_mrp(self,mrp_id):
        consumido=False
        if mrp_id:
            total = len(mrp_id.move_raw_ids)
            total_consumido = 0
            for mv in mrp_id.move_raw_ids:
                if mv.as_consumido == True:
                    total_consumido+=1
            if total_consumido == total:
                mrp_id.open_produce_product()
                mo = mrp_id
                produce_form = Form(self.env['mrp.product.produce'].with_context({'active_id': mo.id,'active_ids': [mo.id],'default_finished_lot_id': mrp_id.as_lot.id,}))
                produce_wizard = produce_form.save()
                produce_wizard.do_produce()
                mrp_id.button_mark_done()
        return True

    # def _get_lotes_lines(self):
    #     resultado = ''
    #     for move in self[0]:
    #         for move_line in move.move_line_ids:
    #             for lots in move_line.lot_produced_ids:
    #                 resultado += lots.name +', '
    #     self.as_lotes = resultado




    