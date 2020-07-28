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
        return BeautifulSoup(text,"html.parser").text

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

    def create_quality_from_picking(self):
        for move in self.move_ids_without_package:
            move._create_quality_checks_from_picking()
        self.as_generate_control =True

    def button_validate(self):
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
        return res