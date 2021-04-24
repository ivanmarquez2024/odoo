# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class Decimales(models.Model):
    _inherit = 'quality.check'

    as_decimales = fields.Char(string='Decimales')

class Decimales(models.Model):
    _inherit = 'quality.point'

    as_decimales_num = fields.Char(string='Decimales')
