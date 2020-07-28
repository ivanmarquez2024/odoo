# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    as_format_type_id = fields.Many2one(comodel_name='product.certificate.format', string='Tipo Certificado')
    as_color = fields.Char(string='Color')


class Productformat(models.Model):
    _name = 'product.certificate.format'
    _description = 'tipo de repore de certificado'

    name = fields.Char(string='Nombre')
    as_code = fields.Integer(string='Codigo/secuencia')
    as_slogan = fields.Text(string='Slogan')
    as_code_iso = fields.Char(string='Codigo ISO')
    as_code_iso_lot = fields.Char(string='Codigo ISO lote')
    image = fields.Binary(attachment=True)
    as_sfooter = fields.Text(string='Footer')
