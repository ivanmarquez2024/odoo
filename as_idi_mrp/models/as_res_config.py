from odoo import fields,models,api, _

class res_config(models.TransientModel): 
    _inherit='res.config.settings'
        
    as_factor = fields.Float(string='Factor para accedente de despacho')
    
    @api.model
    def get_values(self):
        res = super(res_config, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(as_factor = float(params.get_param('as_idi_mrp.as_factor',default=5)))
        return res
    
    def set_values(self):
        res = super(res_config,self).set_values()
        ir_parameter = self.env['ir.config_parameter'].sudo()        
        ir_parameter.set_param('as_idi_mrp.as_factor', self.as_factor)
        return res 
        
