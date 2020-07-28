# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models

class as_master_production(models.TransientModel):
    _name="as.master.production"
    _description = "Warehouse Reports by AhoraSoft"
    
    start_date = fields.Date('Desde la Fecha', default=fields.Date.context_today)
    end_date = fields.Date('Hasta la Fecha', default=fields.Date.context_today)
  
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.master.production'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env.ref('as_idi_mrp.as_master_production').report_action(self, data=datas)