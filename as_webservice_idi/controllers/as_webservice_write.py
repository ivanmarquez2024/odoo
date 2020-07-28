# -*- coding: utf-8 -*-
from odoo.tools.translate import _
from odoo import http
from odoo import http
from odoo.http import request
import re
# from tabulate import tabulate
# from bs4 import BeautifulSoup
import json
import sys
import yaml
import logging
_logger = logging.getLogger(__name__)

from werkzeug import urls
from werkzeug.wsgi import wrap_file

def as_convert(txt,digits=50,is_number=False):
    if is_number:
        num = re.sub("\D", "", txt)
        if num == '':
            return 0
        return int(num[0:digits])
    else:
        return txt[0:digits]        

class as_webservice(http.Controller):

    '''
    Clientes WRITE
    {
        "id":123,
        "token":"c70bf37cbc0f4d758cc4651b4f999c6c",
        "name":"1111Test",
        "phone":"1111",
        "street":"1111",
        "email":"1111@gmail.com",
        "rfc":"valid_rfc"
    }
    '''
    @http.route(["/tiamericas/clientes/write/"], auth='public', type="json", methods=['POST'],csrf=False)
    def partner(self, partner_id = None, **pdata):
        post = yaml.load(request.httprequest.data)

        el_token = post['token'] or 'sin_token'
        current_user = request.env['res.users'].sudo().search([('as_token', '=', el_token)])
        if not current_user:
            res_json = json.dumps({'error': ('Token Invalido')})
            callback = post.get('callback')
            return '{0}({1})'.format(callback, res_json)  
        if current_user:
            if post:
                partner = int(post.get('id')) if post.get('id') else 0
                current_partner = request.env['res.partner'].sudo().search([('id', '=', partner)])
                res = {}
                partner_data = {
                    "name": as_convert(post.get('name') or ""), #Nombre cliente
                    "phone": as_convert(post.get('phone') or "", is_number=True), #Telefono
                    "street": as_convert(post.get('street') or ""), #Direccion
                    "email": as_convert(post.get('email') or ""), #Email
                    "vat": as_convert(post.get('rfc') or ""), #Email
                }
                if not current_partner:
                    new_id = request.env['res.partner'].sudo().create(partner_data)
                    res['status'] = 'Create Successfully'
                    res['id'] = new_id.id
                    res_json = json.dumps(res)
                elif current_partner:
                    current_partner.update(partner_data)
                    res['status'] = 'Update Successfully'
                    res['id'] = current_partner.id
                    res_json = json.dumps(res)
        callback = post.get('callback')
        return '{0}({1})'.format(callback, res_json)

    '''
    PRODUCTOS WRITE
    {
    "product_id": 1425,
    "name": "Papa Frita3",
    "type": "product",
    "categ_id": 1,
    "as_tipo_producto_idi": "bmc",
    "color": "rosado",
    "default_code": "cod-111-abc",
    "codigo_barras": "1234567893",
    "precio_venta": 111.11,
    "costo": 111.11,
    "taxes_id": 1,
    "uom_id": 3,
    "uom_po_id": 3,
    "token": "c70bf37cbc0f4d758cc4651b4f999c6c",
    "purchase_ok": true,
    "sale_ok": true
    }
    '''
    @http.route(["/tiamericas/productos/write/"], auth='public', type="json", methods=['POST'],csrf=False)
    def product(self, product_id = None, **pdata):
        post = yaml.load(request.httprequest.data)
        el_token = post.get('token') or 'sin_token'
        current_user = request.env['res.users'].sudo().search([('as_token', '=', el_token)])
        if not current_user:
            res_json = json.dumps({'error': ('Token Invalido')})
            callback = post.get('callback')
            return '{0}({1})'.format(callback, res_json)  
        if current_user:
            if post:
                product = int(post.get('product_id')) if post.get('product_id') else 0
                current_product = request.env['product.template'].sudo().search([('id', '=', product)])
                res = {}
                product_data = {
                    "name": as_convert(post.get('name') or ""),
                    "type": as_convert(post.get('type') or ""),
                    "categ_id": (post.get('categ_id') or ""),
                    "as_tipo_producto_idi": as_convert(post.get('tipo_producto_idi') or ""),
                    "as_color": as_convert(post.get('color') or ""),
                    "default_code": as_convert(post.get('default_code') or ""),
                    "barcode": as_convert(post.get('codigo_barras') or ""),
                    "list_price": float(post.get('precio_venta') or 0),
                    "standard_price": float(post.get('costo') or 0),
                    "taxes_id": [[6, False, [int(post.get('taxes_id') or 0)]]],
                    "uom_id": int(post.get('uom_id') or 0),
                    "uom_po_id": int(post.get('uom_po_id') or 0),
                    "purchase_ok": (post.get('purchase_ok') or False),
                    "sale_ok": (post.get('sale_ok') or False),
                }
                if not current_product:
                    new_id = request.env['product.template'].sudo().create(product_data)
                    res['status'] = 'Create Successfully'
                    res['id'] = new_id.id
                    res_json = json.dumps(res)
                elif current_product:
                    current_product.update(product_data)
                    res['status'] = 'Update Successfully'
                    res['id'] = current_product.id
                    res_json = json.dumps(res)
        callback = post.get('callback')
        return '{0}({1})'.format(callback, res_json)

    # BOM WRITE
    '''
    {
        "bom_id": 24906,
        "product_tmpl_id": 1423,
        "product_qty": 1.3,
        "code": "Referencia X2",
        "type": "normal",
        "token": "c70bf37cbc0f4d758cc4651b4f999c6c",
        "bom_line_ids":[
            {
            "product_id": 10,
            "product_qty": 667,
            "sequence": 1
            },
            {
            "product_id": 1,
            "product_qty": 777,
            "sequence": 2
            },
            {
            "product_id": 1411,
            "product_qty": 888,
            "sequence": 3
            }
        ]
    }
    '''
    @http.route(["/tiamericas/bom/write/"], auth='public', type="json", methods=['POST'],csrf=False)
    def bom(self, bom_id = None, **pdata):
        post = yaml.load(request.httprequest.data)
        el_token = post.get('token') or 'sin_token'
        current_user = request.env['res.users'].sudo().search([('as_token', '=', el_token)])
        if not current_user:
            res_json = json.dumps({'error': ('Token Invalido')})
            callback = post.get('callback')
            return '{0}({1})'.format(callback, res_json)
        if current_user:
            if post:
                bom = int(post.get('bom_id')) if post.get('bom_id') else 0
                current_boom = request.env['mrp.bom'].sudo().search([('id', '=', bom)])
                res = {}
                bom_data = {
                    'product_tmpl_id': int(post.get('product_tmpl_id') or 0),
                    'product_qty': float(post.get('product_qty') or 0),
                    'code': as_convert(post.get('code') or ""),
                    'type': as_convert(post.get('type') or ""),
                    'bom_line_ids':  [(0, 0, line) for line in post.get('bom_line_ids')], # INSERTAR VARIAS LINEAS A MODELO
                }
                if not current_boom:
                    new_id = request.env['mrp.bom'].sudo().create(bom_data)
                    res['status'] = 'Create Successfully'
                    res['id'] = new_id.id
                    res_json = json.dumps(res)
                elif current_boom:
                    unlink_bom_lines = request.env['mrp.bom.line'].sudo().search([('bom_id', '=', current_boom.id)]).unlink()

                    current_boom.update(bom_data)
                    res['status'] = 'Update Successfully'
                    res['id'] = current_boom.id
                    res_json = json.dumps(res)
        callback = post.get('callback')
        return '{0}({1})'.format(callback, res_json)

    # MRP WRITE
    '''
    {
        "mrp_id": 123,
        "name": "127",
        "as_sale": 1,
        "product_id": 686,
        "bom_id": 1,
        "as_lot": 1,
        "date_planned_start": "2020-01-10",
        "main_mo_id": 1,
        "as_lote_numero": 123,
        "as_lote_peso": 123.123,
        "as_tanque": 123,
        "token": "c70bf37cbc0f4d758cc4651b4f999c6c",
        "product_uom_id": 3
    }
    '''
    @http.route(["/tiamericas/mrp/write/"], auth='public', type="json", methods=['POST'],csrf=False)
    def mrp(self, bom_id = None, **pdata):
        post = yaml.load(request.httprequest.data)
        el_token = post.get('token') or 'sin_token'
        current_user = request.env['res.users'].sudo().search([('as_token', '=', el_token)])
        if not current_user:
            res_json = json.dumps({'error': ('Token Invalido')})
            callback = post.get('callback')
            return '{0}({1})'.format(callback, res_json)
        if current_user:
            if post:
                mrp = int(post.get('mrp_id')) if post.get('mrp_id') else 0
                current_mrp = request.env['mrp.production'].sudo().search([('id', '=', mrp)])
                res = {}
                mrp_data = {
                    'name': as_convert(post.get('name') or ""),
                    'as_sale': int(post.get('as_sale') or ""),
                    'product_id': int(post.get('product_id') or ""),
                    'bom_id': int(post.get('bom_id') or ""),
                    'as_lot': int(post.get('as_lot') or ""),
                    'date_planned_start': as_convert(post.get('date_planned_start') or ""),
                    'main_mo_id': int(post.get('main_mo_id') or ""),
                    'as_lote_numero': int(post.get('as_lote_numero') or ""),
                    'as_lote_peso': float(post.get('as_lote_peso') or ""),
                    'as_tanque': int(post.get('as_tanque') or ""),
                    'product_uom_id': int(post.get('product_uom_id') or ""),
                    # 'move_raw_ids': "",
                }

                if not current_mrp:
                    new_id = request.env['mrp.production'].sudo().create(mrp_data)
                    new_id.sudo()._onchange_move_raw()
                    new_id.sudo()._onchange_bom_id()
                    new_id.sudo().onchange_product_id()
                    new_id.sudo().onchange_company_id()
                    new_id.sudo().onchange_picking_type()
                    
                    new_id.sudo()._onchange_date_planned_start()
                    res['status'] = 'Create Successfully'
                    res['id'] = new_id.id
                    res_json = json.dumps(res)
                elif current_mrp:
                    unlink_bom_lines = request.env['mrp.production.line'].sudo().search([('mrp_id', '=', current_mrp.id)]).unlink()

                    current_mrp.update(mrp_data)
                    res['status'] = 'Update Successfully'
                    res['id'] = current_mrp.id
                    res_json = json.dumps(res)
        callback = post.get('callback')
        return '{0}({1})'.format(callback, res_json)

    # CONTENEDOR WRITE
    '''
    {
    "id": 10,
    "token": "c70bf37cbc0f4d758cc4651b4f999c6c",
    "as_contenedor_id":[
            {
                "name": "1211",
                "as_pesob_kg": 33.3,
                "as_peson_kg": 31.1,
                "as_pesob_lb": 34.4,
                "as_peson_lb": 32.2,
                "as_lote":[1,2,3]
            },
            {
                "name": "2122",
                "as_peson_kg": 41.11,
                "as_peson_lb": 42.22,
                "as_pesob_kg": 43.33,
                "as_pesob_lb": 44.44,
                "as_lote":[4,5,6]
            }
        ]
    }
    '''
    @http.route(["/tiamericas/wh/contenedor/"], auth='public', type="json", methods=['POST'],csrf=False)
    def whcontenedor(self, bom_id = None, **pdata):
        post = yaml.load(request.httprequest.data)
        el_token = post.get('token') or 'sin_token'
        current_user = request.env['res.users'].sudo().search([('as_token', '=', el_token)])
        if not current_user:
            res_json = json.dumps({'error': ('Token Invalido')})
            callback = post.get('callback')
            return '{0}({1})'.format(callback, res_json)
        if current_user:
            if post:
                wh = int(post.get('id')) if post.get('id') else 0
                current_picking = request.env['stock.picking'].sudo().search([('id', '=', wh)])
                
                res = {}
                wh_data = {
                    'as_contenedor_id':  [(0, 0, line) for line in post.get('as_contenedor_id')]
                }

                if current_picking:
                    unlink_as_contenedor_id_lines = request.env['as.contenedor'].sudo().search([('picking_id', '=', current_picking.id)]).unlink()

                    current_picking.update(wh_data)
                    res['status'] = 'Update Successfully'
                    res['id'] = current_picking.id
                    res_json = json.dumps(res)
        callback = post.get('callback')
        return '{0}({1})'.format(callback, res_json)

    # MRP QTY DONE WRITE
    '''
    {
        "id": 123,
        "token": "c70bf37cbc0f4d758cc4651b4f999c6c",
        "quantity_done": 111,
        "lot_name": "2020-0002"
    }
    '''
    @http.route(["/tiamericas/mrp/consumido/"], auth='public', type="json", methods=['POST'],csrf=False)
    def mrpconsumido(self, bom_id = None, **pdata):
        post = yaml.load(request.httprequest.data)
        el_token = post.get('token') or 'sin_token'
        lot_name = post.get('lot_name') or ''
        current_user = request.env['res.users'].sudo().search([('as_token', '=', el_token)])
        lot_id = request.env['stock.production.lot'].sudo().search([('name', '=', lot_name)])
        if not current_user:
            res_json = json.dumps({'error': ('Token Invalido')})
            callback = post.get('callback')
            return '{0}({1})'.format(callback, res_json)
        if current_user:
            if post:
                quantity_done = float(post.get('quantity_done')) if post.get('quantity_done') else 0
                wh = int(post.get('id')) if post.get('id') else 0
                current_move = request.env['stock.move'].sudo().search([('id', '=', wh)])
                
                res = {}
                wh_data = {
                    'quantity_done':  quantity_done,
                    'as_lotes':  lot_name
                }

                if current_move:
                    current_move.update(wh_data)
                    res['status'] = 'Update Successfully'
                    res['id'] = current_move.id
                    res_json = json.dumps(res)
        callback = post.get('callback')
        return '{0}({1})'.format(callback, res_json)

    # Convertir objeto a json
    # Fields debe tener al menos 2 valores
    def obj_to_json(self, objeto, fields = None):
        json_dict = []
        rp = {}
        rp2 = []
        if fields:
            if objeto:
                for child in objeto:
                    rp = {}
                    for field in fields:
                        if isinstance(getattr(child, field), (float, int, str)):
                            rp[field] = getattr(child, field)
                        else:
                            rp[field] = self.obj_to_json(getattr(child, field))
                    rp2.append(rp)
                json_dict.append(rp2)
            else:
                json_dict = {'error': _('Not found')}               
        else:
            if objeto:
                for child in objeto:
                    json_dict.append({
                        "id": child.id,
                        "name": child.name, #Nombre cliente
                    })
            else:
                json_dict = {'error': _('Not found')}
        return json_dict

