# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'quality.check'

    # def printer_report(self):
    #     self.ensure_one()
    #     data = {'ids': self.env.context.get('active_ids', [])}
    #     res = self.read()
    #     res = res and res[0] or {}
    #     data.update({'form': res})
    #     return self.env.ref('as_idi_mrp.report_certificate_idi').report_action(self, data=data)

    def printer_report(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'quality.check'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env.ref('as_idi_mrp.report_certificate_idi').report_action(self, data=datas)
        