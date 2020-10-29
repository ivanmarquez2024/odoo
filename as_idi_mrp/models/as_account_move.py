# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import time
import datetime
from time import mktime
from dateutil import parser
from datetime import datetime, timedelta, date

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "account.move"

    as_order_partner = fields.Char(string='Nro orden cliente',required=True,default='P0001')

