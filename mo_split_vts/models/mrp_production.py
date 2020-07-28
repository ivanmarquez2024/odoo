from odoo import api, fields, models, _
    
class ManufacturingOrder(models.Model):
    _inherit = 'mrp.production'
    
    main_mo_id = fields.Many2one('mrp.production',string='Source MO')
    
    def open_slip_wizard(self):
        context = dict(self._context or {})
        context['default_split_mo_lot']=self.as_lote_numero 
        context['active_id']=self.id 
        context['active_model']= 'mrp.production'
        return {
            'name': _("Produccion %s") % self.display_name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [[self.env.ref('mo_split_vts.split_manufacture_order_form_view').id, 'form']],
            'res_model': 'split.mo',
            'target': 'new',
            'context': context,
        }
       
    def action_confirm(self):
        res = super(ManufacturingOrder, self).action_confirm()
        for production in self:
            if production.check_ids and production.as_lot:
                for ckeck in production.check_ids:
                    ckeck.write({'lot_id':production.as_lot.id})
        return res    
    
    def action_assign(self):
        res = super(ManufacturingOrder, self).action_assign()
        for production in self:
            if production.check_ids and production.as_lot:
                for ckeck in production.check_ids:
                    ckeck.write({'lot_id':production.as_lot.id})
        return res

