# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class as_product_template(models.Model):
    _inherit = 'product.template'
   
    valores = [
                ('bmc','bmc'),
                ('smc','smc'),
                ('resinas','resinas'),
                ('aditivos','aditivos'),
                ('aditivos_especiales','aditivos_especiales'),
                ('internal','internal'),
                ('catalizadores','catalizadores'),
                ('inhibidores','inhibidores'),
                ('desmoldantes','desmoldantes'),
                ('pigmentos','pigmentos'),
                ('cargas_minerales','cargas_minerales'),
                ('refuerzos','refuerzos'),
                ('empaque','empaque'),
                ('otros','otros'),
            ]

    as_tipo_producto_idi = fields.Selection(valores, string='Tipo De Producto IDI')
    as_color = fields.Char(string='Color')
    

