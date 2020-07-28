from odoo import fields,models,api

class res_config(models.TransientModel): 
    _inherit='res.config.settings'
        
    mo_split_based_on = fields.Selection([('based_on_number_of_split','Number Of Split'),('based_on_number_of_qty','Number Of Qty')],default='based_on_number_of_qty',string='Split MO Based On')
    
    @api.model
    def get_values(self):
        res = super(res_config, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(mo_split_based_on = params.get_param('mo_split_vts.mo_split_based_on',default='based_on_number_of_split'))
        return res
    
    def set_values(self):
        super(res_config,self).set_values()
        ir_parameter = self.env['ir.config_parameter'].sudo()        
        ir_parameter.set_param('mo_split_vts.mo_split_based_on', self.mo_split_based_on)
        
