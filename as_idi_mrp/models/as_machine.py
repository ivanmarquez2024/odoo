
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils, float_compare    
from datetime import datetime, timedelta, date

import logging
_logger = logging.getLogger(__name__)

class as_mrp_workorder(models.Model):
    _name = "as.machine"
    
    as_numero = fields.Char(string='Numero')
    name = fields.Char(string='Nombre')
    as_min = fields.Float(string='Capacidad Minima')
    as_max = fields.Float(string='Capacidad Maxima')
    sequence_id = fields.Many2one("ir.sequence", string='Secuencia', ondelete='cascade')

