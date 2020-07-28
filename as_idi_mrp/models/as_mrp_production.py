# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils, float_compare    
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError
import logging
from odoo.exceptions import Warning, UserError, AccessError
_logger = logging.getLogger(__name__)

class as_mrp_workorder(models.Model):
    _inherit = "mrp.production"

    # @api.depends('as_sale')
    # def get_salidas_sales(self):
    #     for mrp in self:
    #         picking = self.env['stock.picking'].search([('origin', '=', mrp.origin)])
    #         if picking:
    #             mrp.as_picking_id = picking.ids

    
    as_machine_id = fields.Many2one(comodel_name='as.machine', string='Maquina')
    as_lote_numero = fields.Integer(string='Cantidad Lote')
    as_lote_peso = fields.Float(string='Peso x Lote')
    as_tanque = fields.Integer(string='Tanque')
    as_sale = fields.Many2one('sale.order', 'Venta Origen', readonly=True)
    as_lot = fields.Many2one('stock.production.lot', 'Nro Lote',
    domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]",readonly=True)
    as_picking_id = fields.Many2many('stock.picking', string ='Salidas Relacionada a las ventas')
    as_cliente_venta = fields.Char(string='Cliente Venta')

    def check_all_state_mo(self):
        sales = self.env['mrp.production'].search([('state', '=','to_close')])
        for mo in sales:
            mo.write({'state':'done'})
        return True

    def open_produce_product(self):
        self.ensure_one()
        if self.bom_id.type == 'phantom':
            raise UserError(_('You cannot produce a MO with a bom kit product.'))
        action = self.env.ref('mrp.act_mrp_product_produce').read()[0]
        action.update({
            'context': {
                'default_finished_lot_id': self.as_lot.id,
               
            },
        })
        return action  

    @api.model
    def create(self, vals):
        if 'origin' in vals:
            sale = self.env['sale.order'].search([('name', '=', vals['origin'])])
            if sale:
                vals['as_sale']= sale.id
        picking_type = super(as_mrp_workorder, self).create(vals)
        return picking_type

    @api.depends('origen')
    def onchange_as_origen(self):
        sale = self.env['sale.order'].search([('name', '=', self.origin)])
        picking = self.env['stock.picking'].search([('origin', '=', sale.name)])
        if sale:
            self.write({'as_sale':sale.id})

    @api.onchange('as_lote_numero','as_tanque')
    def onchange_as_tanque(self):
        for order in self:
            if order.as_tanque > order.as_lote_numero:
                raise Warning("La cantidad de Tanque no puede ser mayor a la cantidad de lote")
                order.as_tanque = 0

    @api.onchange('as_lote_peso')
    def onchange_as_peso_lote(self):
        for order in self:
            macine= order.as_machine_id.as_numero
            macine_max= order.as_machine_id.as_max
            macine_min= order.as_machine_id.as_min
            if macine:
              if order.as_lote_peso < float(macine_min) or order.as_lote_peso > float(macine_max):
                raise Warning("Cantidad fuera de la capacidad de la maquina")
                order.as_lote_peso = 0.0                
            else:
                raise Warning("Debe seleccionar una maquina")
                order.as_lote_peso = 0.0

class asMRP(models.Model):
    _inherit = 'stock.move'

    as_lotes = fields.Char(string='Lotes')
    

    # def _get_lotes_lines(self):
    #     resultado = ''
    #     for move in self[0]:
    #         for move_line in move.move_line_ids:
    #             for lots in move_line.lot_produced_ids:
    #                 resultado += lots.name +', '
    #     self.as_lotes = resultado




    