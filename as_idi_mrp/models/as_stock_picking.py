# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import time
import datetime
from time import mktime
from dateutil import parser
from datetime import datetime, timedelta, date
#QR
import qrcode
from bs4 import BeautifulSoup
import tempfile
import base64
from io import StringIO
import io
import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    as_contenedor_id = fields.One2many('as.contenedor', 'picking_id', string='Rules', help='The list of barcode rules')
    as_generate_control= fields.Boolean(string='Bandera de controles',default=False) 
    as_stock_extra = fields.Many2one('stock.picking', string='Movimiento Remanente')

    def get_actualiza_default_code(self,lot_id,name):
        lot_id.update({'ref':name,'lot_name':name})

    @api.model
    def create(self, vals):
        ids = []
        picking = super(StockPicking, self).create(vals)
        if picking:
            sale = self.env['sale.order'].search([('name', '=', picking.origin)])
            if sale:
                mrps = self.env['mrp.production'].search([('origin', '=', sale.name)])
                ids.append(picking.id)
                pickings = self.env['stock.picking'].search([('origin', '=', sale.name)])
                ids + pickings.ids
                for mrp in mrps:
                    mrp.as_picking_id=ids
        return picking


    # def write(self, vals):
    #     result = super(StockPicking, self).write(vals)
    #     for rec in self:
    #         lotes_comprometidos = []
    #         for contenedor in rec.as_contenedor_id:
    #             if contenedor.as_entregado == True:
    #                 for lot in contenedor.as_lote:
    #                     lotes_comprometidos.append(lot.id)
    #         for contenedor in rec.as_contenedor_id:
    #             if contenedor.as_entregado == False:
    #                 for lot in contenedor.as_lote:
    #                     if lot.id not in lotes_comprometidos:
    #                         for move_line in rec.move_line_ids_without_package:
    #                             if move_line.lot_id.id == lot.id:
    #                                 move_line.unlink()
    #     return result

    def get_qrcode(self,cadena_qr): 
        try:
            qr_img = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=10,border=0)
            qr_img.add_data(cadena_qr)
            qr_img.make(fit=True)
            img = qr_img.make_image()
            # buffer = StringIO()
            buffer = io.BytesIO()
            img.save(buffer)
            qr_img = base64.b64encode(buffer.getvalue())
            return qr_img
        except:
            raise UserError(_('No se puedo generar el codigo QR'))

    def get_format(self,number):
        if number <10:
            return '0'+str(number)
        else:
            return str(number)

    def get_partner_id(self):
        return self.env.user.partner_id.name

    def get_pobs(self,text):
        textstr = ''
        if text:
            textstr = BeautifulSoup(text,"html.parser").text
        return textstr

    def get_sale_name(self):
        venta =''
        sale = self.env['sale.order'].search([('name', '=', self.origin)],limit=1)
        if sale:
            venta = sale.as_order_partner
        return venta

    def totales(self):
        as_pesob_kg = 0.0
        as_peson_kg = 0.0
        as_pesob_lb = 0.0
        as_peson_lb = 0.0
        for pick in self.as_contenedor_id:
            if pick.as_entregado:
                as_pesob_kg += pick.as_pesob_kg
                as_peson_kg += pick.as_peson_kg
                as_pesob_lb += pick.as_pesob_lb
                as_peson_lb += pick.as_peson_lb
        vals = {
            'as_pesob_kg': as_pesob_kg,
            'as_peson_kg': as_peson_kg,
            'as_pesob_lb': as_pesob_lb,
            'as_peson_lb': as_peson_lb,
        }
        return vals
    # def get_name_picking(self,move_id):
    #     name=''
    #     move_line_id = self.env['stock.move.line'].search([('id', '=', move_id)])

    def as_get_lote_done(self):
        for move in self.move_line_ids_without_package:
            move.product_uom_qty = 0
            move.qty_done = 0
        self.move_line_ids_without_package.unlink()
        venta = self.env['sale.order'].search([('name', '=', self.origin)])
        move_lines = []
        presentes = []
        for move in self.move_ids_without_package:
            cantidad = move.product_uom_qty
            mrps = self.env['mrp.production'].search([('as_sale', '=', venta.id),('state', '=', 'done'),('product_id', '=', move.product_id.id),('as_quality_cien', '=', True),('as_usage', '=', False)])
            if mrps:
                for mrp in mrps:
                    if mrp.as_lot.product_qty <= cantidad:
                        cantidad -= mrp.as_lot.product_qty
                        presentes.append(mrp.as_lot.id)
                        vals = {
                            'product_id': mrp.product_id.id,
                            'product_uom_id': move.product_uom.id,
                            'location_id': move.location_id.id,
                            'location_dest_id': move.location_dest_id.id,
                            'lot_id': mrp.as_lot.id,
                            'picking_id': self.id,
                            'move_id': move.id,
                            'as_mo_id': mrp.id,
                            'qty_done': mrp.as_lot.product_qty,
                            # 'product_uom_qty': mrp.as_lot.product_qty,
                        }
                        move_lines.append(vals)
            mrps_usados = self.env['mrp.production'].search([('as_sale', '=', venta.id),('state', '=', 'done'),('product_id', '=', move.product_id.id),('as_quality_cien', '=', True),('as_usage', '=', True)])
            if mrps_usados:
                for mrp_usados in mrps_usados:
                    presentes.append(mrp_usados.as_lot.id)
        for contender in self.as_contenedor_id:
            total = 0
            for lot in presentes:
                if lot in contender.as_lote.ids:
                    total += 1
            if total == len(contender.as_lote.ids):
                contender.as_entregado = True
            else:
                contender.as_entregado = False


        if move_lines != []:
            self.env['stock.move.line'].sudo().create(move_lines)
        #separando contenedores



    def create_quality_from_picking(self):
        for move in self.move_ids_without_package:
            if self.state == 'done':
                move._create_quality_checks_from_picking()
            else:
                move._create_quality_checks_from_picking_after()

        self.as_generate_control =True
        for check_id in self.check_ids:
            for move in self.move_lines:
                for move_lines in move.move_line_nosuggest_ids:
                    if move_lines.lot_id.name == check_id.as_lot_name:
                        check_id.lot_id = move_lines.lot_id
                        move_lines.lot_id.as_lot_supplier = move_lines.as_lot_supplier

        for move in self.move_lines:
            for move_lines in move.move_line_nosuggest_ids:
                move_lines.lot_id.as_lot_supplier = move_lines.as_lot_supplier

    def button_validate(self):
        if self.picking_type_id.code =='outgoing':
            # comentada funcionalidad de restriccion de lotes si no tienen control de calidad
            for move in self.move_ids_without_package:
                for line_move in move.move_line_ids:
                    if not line_move.lot_id.as_quality_control:
                        raise UserError(_('No puede hacer uso de un lote que no ha completado control de calidad %s')%str(line_move.lot_id.name))
            for move in self.move_line_ids_without_package:
                if not move.lot_id.as_quality_control:
                        raise UserError(_('No puede hacer uso de un lote que no ha completado control de calidad %s')%str(move.lot_id.name))
        res = super(StockPicking, self).button_validate()
        for check_id in self.check_ids:
            for move in self.move_lines:
                for move_lines in move.move_line_nosuggest_ids:
                    if move_lines.lot_id.name == check_id.as_lot_name:
                        check_id.lot_id = move_lines.lot_id
                        move_lines.lot_id.as_lot_supplier = move_lines.as_lot_supplier

        for move in self.move_lines:
            for move_lines in move.move_line_nosuggest_ids:
                move_lines.lot_id.as_lot_supplier = move_lines.as_lot_supplier
        for contender in self.as_contenedor_id:
            if contender.as_entregado:
                for lot in contender.as_lote:
                    if not lot.as_quality_control:
                        raise UserError(_('El lote %s no posee Controles de Calidad realizados')%str(lot.name))
        if self.picking_type_id.code =='outgoing':
            #marcar como usado las lineas detalladas 
            for line in self.move_line_ids_without_package:
                line.as_mo_id.as_usage = True
            total_ope = 0.0
            total_ini = 0.0
            picking_anterior = self
            for line in picking_anterior.move_line_ids_without_package:
                total_ope+= line.qty_done
            for line_move in picking_anterior.move_ids_without_package:
                total_ini+= line_move.product_uom_qty
            if total_ini == total_ope:
                picking_anterior.as_generate_remanente()
        return res

    def as_generate_remanente(self):
        for contenedor in self.as_contenedor_id:
            qty = float(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_factor')) or 0.001
            if not contenedor.as_entregado and not self.as_stock_extra:
                picking = self.env['stock.picking'].create({
                    'partner_id': self.partner_id.id,
                    'picking_type_id': self.picking_type_id.id,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.location_dest_id.id,
                    'origin': self.origin,
                    'sale_id': self.sale_id.id,
                })
                for line in self.move_ids_without_package:
                    move_id = self.env['stock.move'].create({
                        'name':line.product_id.name,
                        'location_id': line.location_id.id,
                        'location_dest_id': line.location_dest_id.id,
                        'product_id':line.product_id.id,
                        'product_uom':line.product_id.uom_id.id,
                        'product_uom_qty': qty,
                        'quantity_done': qty,
                        'picking_id': picking.id,
                    })
                    # self.env['stock.move.line'].create({
                    #     'location_id': line.location_id.id,
                    #     'location_dest_id': line.location_dest_id.id,
                    #     'product_id':line.product_id.id,
                    #     'product_uom_id':line.product_id.uom_id.id,
                    #     'move_id': move_id.id,
                    #     'lot_id': contenedor.as_lote[0].id,
                    #     'qty_done': qty,
                    #     'picking_id': picking.id,
                    # })
                for line in picking.move_line_ids_without_package:
                    if len(contenedor.as_lote) > 0:
                        line.lot_id = contenedor.as_lote[0].id
                picking.action_confirm()



                # Process the delivery of the outgoing shipment
                # self.env['stock.immediate.transfer'].create({'pick_ids': [(4, picking.id)]}).process()
                vals = {
                    "name": contenedor.name ,
                    "as_pesob_kg": contenedor.as_pesob_kg,
                    "picking_id": picking.id,
                    "as_entregado": True,
                    "as_peson_kg": contenedor.as_peson_kg,
                    "as_pesob_lb": contenedor.as_pesob_lb,
                    "as_peson_lb": contenedor.as_peson_lb,
                    "as_lote": contenedor.as_lote.ids,
                }
                contenido = self.env['as.contenedor'].create(vals)

                # for contenedor_r in self.as_contenedor_id:
                #     if not contenedor_r.as_entregado:
                #         vals = {
                #             "name": contenedor_r.name ,
                #             "as_pesob_kg": contenedor_r.as_pesob_kg,
                #             "picking_id": picking.id,
                #             "as_entregado": True,
                #             "as_peson_kg": contenedor_r.as_peson_kg,
                #             "as_pesob_lb": contenedor_r.as_pesob_lb,
                #             "as_peson_lb": contenedor_r.as_peson_lb,
                #             "as_lote": contenedor_r.as_lote.ids,
                #         }
                #         contenido = self.env['as.contenedor'].create(vals)