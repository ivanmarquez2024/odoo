# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import time
import datetime
from time import mktime
from dateutil import parser
from datetime import datetime, timedelta, date

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    as_cantidad_mo = fields.Float('MO', compute='_get_lotes_lines')
    as_order_partner = fields.Char(string='Nro orden cliente',required=True,default='P0001')
    
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['as_order_partner'] = self.as_order_partner
        return invoice_vals

    def _get_lotes_lines(self):
        resultado = 0
        mo = self.env['mrp.production'].search([('origin', '=', self.name)])
        if mo:
            mos = self.env['mrp.production'].search([('origin', '=', mo.name)])
            self.as_cantidad_mo = len(mo)+len(mos)
        else:
            self.as_cantidad_mo = 0

    def open_entries(self):
        ids =[]
        mos = self.env['mrp.production']
        mo = self.env['mrp.production'].search([('origin', '=', self.name)])
        if mo:
            mos = self.env['mrp.production'].search([('origin', '=', mo.name)])
            for order in mo:
                ids.append(order.id)
            if mos:
                for order2 in mos:
                    ids.append(order2.id)
        return {
            'name': _('Producciones'),
            'view_mode': 'tree',
            'res_model': 'mrp.production',
            'views': [(self.env.ref('mrp.mrp_production_tree_view').id, 'tree'), (False, 'form')],
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', tuple(ids))],
            'context': dict(self._context, create=False),
        }

class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    as_lot_supplier = fields.Char(string='Lote Proveedor')
    as_quality_control = fields.Boolean('Realizado Control de Calidad', default=False)