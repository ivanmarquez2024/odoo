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

class Contenedor(models.Model):
    _name = "as.contenedor"

    name = fields.Char(string='Nombre Contenedor')
    as_pesob_kg = fields.Float(string='Peso Bruto kg')
    as_peson_kg = fields.Float(string='Peso Neto kg')    
    as_pesob_lb = fields.Float(string='Peso Bruto lb')
    as_peson_lb = fields.Float(string='Peso Neto lb')
    as_lote = fields.Many2many('stock.production.lot', string='Nro Lote')
    picking_id = fields.Many2one(comodel_name='stock.picking', string='Picking_id')

    @api.onchange('as_pesob_kg')
    def get_udm_conversion(self):
        udm_kg = self.env['uom.uom'].search([('name', '=', 'kg')])
        self.as_pesob_lb = udm_kg._compute_quantity(self.as_pesob_kg, self.env.ref('uom.product_uom_lb'))

    @api.onchange('as_peson_kg')
    def get_udm_conversionn(self):
        udm_kg = self.env['uom.uom'].search([('name', '=', 'kg')])
        self.as_peson_lb = udm_kg._compute_quantity(self.as_peson_kg, self.env.ref('uom.product_uom_lb'))
        
