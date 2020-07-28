# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class res_partner(models.Model):
    _inherit = 'res.partner'

    as_pr_nro = fields.Char(string="Customer Prod. Nr")
    as_internacional = fields.Boolean(string="Es Internacional")