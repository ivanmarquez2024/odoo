# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class Box(models.Model):
    _inherit = 'quality.check'

    as_box = fields.Char(string='Box')