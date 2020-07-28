# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import time
import datetime
from time import mktime
from dateutil import parser
from datetime import datetime, timedelta, date

from collections import defaultdict

from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    as_lot_supplier = fields.Char(string='Lote Proveedor')

    def write(self, values):
        res = super(StockMoveLine, self).write(values)
        
        return res

class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, values):
        res = super(StockMove, self).write(values)
        cont = 1
        for line in self.move_line_nosuggest_ids:
            line.lot_name = str(line.product_id.default_code)+'-'+str(line.picking_id.name)+'-'+str(self.get_format(cont))
            cont+=1
        return res

    def get_format(self,number):
        if number <10:
            return '0'+str(number)
        else:
            return str(number)

    @api.onchange('move_line_nosuggest_ids')
    def get_name_lot(self):
        cont = 1
        for line in self.move_line_nosuggest_ids:
            line.lot_name = str(line.product_id.default_code)+'-'+str(line.picking_id.name)+'-'+str(self.get_format(cont))
            cont+=1


    def _create_quality_checks(self):
        # Used to avoid duplicated quality points
        quality_points_list = set([])
        if not self.picking_id:
            pick_moves = defaultdict(lambda: self.env['stock.move'])
            for move in self:
                pick_moves[move.picking_id] |= move

            for picking, moves in pick_moves.items():
                for check in picking.sudo().check_ids:
                    point_key = (check.picking_id.id, check.point_id.id, check.team_id.id, check.product_id.id)
                    quality_points_list.add(point_key)
                quality_points = self.env['quality.point'].sudo().search([
                    ('picking_type_id', '=', picking.picking_type_id.id),
                    '|', ('product_id', 'in', moves.mapped('product_id').ids),
                    '&', ('product_id', '=', False), ('product_tmpl_id', 'in', moves.mapped('product_id').mapped('product_tmpl_id').ids)])
                for point in quality_points:
                    if point.check_execute_now():
                        if point.product_id:
                            point_key = (picking.id, point.id, point.team_id.id, point.product_id.id)
                            if point_key in quality_points_list:
                                continue
                            self.env['quality.check'].sudo().create({
                                'picking_id': picking.id,
                                'point_id': point.id,
                                'team_id': point.team_id.id,
                                'product_id': point.product_id.id,
                                'company_id': picking.company_id.id,
                            })
                            quality_points_list.add(point_key)
                        else:
                            products = picking.move_lines.filtered(lambda move: move.product_id.product_tmpl_id == point.product_tmpl_id).mapped('product_id')
                            for product in products:
                                point_key = (picking.id, point.id, point.team_id.id, product.id)
                                if point_key in quality_points_list:
                                    continue
                                self.env['quality.check'].sudo().create({
                                    'picking_id': picking.id,
                                    'point_id': point.id,
                                    'team_id': point.team_id.id,
                                    'product_id': product.id,
                                    'company_id': picking.company_id.id,
                                })
                                quality_points_list.add(point_key)

    def _create_quality_checks_from_picking(self):
        # Used to avoid duplicated quality points
        quality_points_list = set([])
        pick_moves = defaultdict(lambda: self.env['stock.move'])
        for move in self:
            pick_moves[move.picking_id] |= move

        for picking, moves in pick_moves.items():
            for check in picking.sudo().check_ids:
                point_key = (check.picking_id.id, check.point_id.id, check.team_id.id, check.product_id.id)
                quality_points_list.add(point_key)
            quality_points = self.env['quality.point'].sudo().search([
                ('picking_type_id', '=', picking.picking_type_id.id),
                '|', ('product_id', 'in', moves.mapped('product_id').ids),
                '&', ('product_id', '=', False), ('product_tmpl_id', 'in', moves.mapped('product_id').mapped('product_tmpl_id').ids)])
            for point in quality_points:
                if point.check_execute_now():
                    if point.product_id:
                        point_key = (picking.id, point.id, point.team_id.id, point.product_id.id),
                        if point_key in quality_points_list:
                            continue
                        if moves.product_id.tracking =='lot':
                            if not moves.move_line_nosuggest_ids:
                                raise UserError(_('Hay productos que no poseen lotes, completelos'))
                            for move_line in moves.move_line_nosuggest_ids:
                                self.env['quality.check'].sudo().create({
                                    'picking_id': picking.id,
                                    'point_id': point.id,
                                    'team_id': point.team_id.id,
                                    'as_lot_name': move_line.lot_name,
                                    'product_id': point.product_id.id,
                                    'company_id': picking.company_id.id,
                                })
                                quality_points_list.add(point_key)
                        else:
                            self.env['quality.check'].sudo().create({
                                'picking_id': picking.id,
                                'point_id': point.id,
                                'team_id': point.team_id.id,
                                'as_lot_name': '',
                                'product_id': point.product_id.id,
                                'company_id': picking.company_id.id,
                            })
                            quality_points_list.add(point_key)

                    else:
                        products = picking.move_lines.filtered(lambda move: move.product_id.product_tmpl_id == point.product_tmpl_id).mapped('product_id')
                        for product in products:
                            point_key = (picking.id, point.id, point.team_id.id, product.id)
                            if point_key in quality_points_list:
                                continue
                            if moves.product_id.tracking =='lot':
                                if not moves.move_line_nosuggest_ids:
                                    raise UserError(_('Hay productos que no poseen lotes, completelos'))
                                for move_line in moves.move_line_nosuggest_ids:
                                    self.env['quality.check'].sudo().create({
                                        'picking_id': picking.id,
                                        'point_id': point.id,
                                        'team_id': point.team_id.id,
                                        'as_lot_name': move_line.lot_name,
                                        'product_id': product.id,
                                        'company_id': picking.company_id.id,
                                    })
                                    quality_points_list.add(point_key)
                            else:
                                self.env['quality.check'].sudo().create({
                                    'picking_id': picking.id,
                                    'point_id': point.id,
                                    'team_id': point.team_id.id,
                                    'as_lot_name': '',
                                    'product_id': product.id,
                                    'company_id': picking.company_id.id,
                                })
                                quality_points_list.add(point_key)                               

class QualityCheck(models.Model):
    _inherit = "quality.check"

    as_lot_name = fields.Char(string='Lote Name')