from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import Warning
    
class SplitManufactureOrder(models.TransientModel):
    _name = 'split.mo'
    _description = 'Split Manufacturing Order'
    
    split_mo_lot = fields.Integer(string='Numero de Cant/Split', required=True,help="Split MO Based on Configuration Like Number Of Qty/Lot.based on that split the MO of that Qty and decrease the product qty from Main MO.")
    
    def split_mo(self):
        #creacion anticipado del lote
        mo_obj = self.env['mrp.production']
        copy_mo = mo_obj
        split_mo_based_on = self.env['ir.config_parameter'].sudo().get_param('mo_split_vts.mo_split_based_on')
        if self._context.get('active_id') and self._context.get('active_model')=='mrp.production':
            mo_id = mo_obj.browse(self.env.context['active_id'])
            self.generate_lot(mo_id.id)
            sale = self.env['sale.order'].search([('name', '=', mo_id.origin)])
            if sale:
                mo_id.write({'as_sale':sale.id})
            if mo_id.state not in ('confirmed'):
                raise UserError(_("You can not split MO in state %s "%(mo_id.state)))
            if split_mo_based_on == 'based_on_number_of_split':
                if not (mo_id.product_qty % self.split_mo_lot == 0):
                    raise Warning('Manufacture Order cannot be split into equal parts.')
                split_qty = mo_id.product_qty/self.split_mo_lot
                for x in range(self.split_mo_lot - 1):
                    copy_mo = mo_id.copy({'main_mo_id':mo_id.id})
                    self.generate_lot(copy_mo.id)
                    if sale:
                        copy_mo.write({'as_sale':sale.id})
                    copy_mo.write({'product_qty':split_qty,'origin':mo_id.name})
                    copy_mo.action_confirm()
                    # change_production_qty = self.env['change.production.qty'].create({'mo_id':copy_mo.id,'product_qty':split_qty})
                    # change_production_qty.change_prod_qty()
                    # copy_mo.action_assign()
            else:
                if self.split_mo_lot <= 0:
                    raise Warning('Qty Must be Grater Than Zero.')
                split_qty = mo_id.product_qty - self.split_mo_lot
                copy_mo = mo_id.copy({'main_mo_id':mo_id.id})
                self.generate_lot(copy_mo.id)
                if sale:
                    copy_mo.write({'as_sale':sale.id})
                copy_mo.write({'product_qty':self.split_mo_lot,'origin':mo_id.name})
                copy_mo.action_confirm()
                # change_production_qty = self.env['change.production.qty'].create({'mo_id':copy_mo.id,'product_qty':self.split_mo_lot})
                # change_production_qty.change_prod_qty()
                # copy_mo.action_assign()
            if copy_mo:
                mo_id.write({'product_qty':split_qty,'main_mo_id':copy_mo.id})
            else:
                mo_id.write({'product_qty':split_qty})
            # change_production_qty = self.env['change.production.qty'].create({'mo_id':mo_id.id,'product_qty':split_qty})
            # change_production_qty.change_prod_qty()
            return True

    def generate_lot(self,production):
        production_id = self.env['mrp.production'].search([('id', '=', production)])
        production_id.as_lot = self.env['stock.production.lot'].create({
            'product_id': production_id.product_id.id,
            'company_id': production_id.company_id.id
        })
        name = str(production_id.product_id.categ_id.as_code_orden)
        machine = production_id.as_machine_id.as_numero  
        if not machine:
            machine = 'ND'
        tipo_material = production_id.as_lot.name
        if not production_id.as_machine_id.sequence_id:
            raise Warning('La maquina seleccionada debe tener secuencia registrada.')
        new_name = production_id.as_machine_id.sequence_id.next_by_id()
        production_id.as_lot.write({
            'name': new_name
        })
        #asignar lote a controles de calidad
        for ckeck in production_id.check_ids:
            ckeck.write({'lot_id':production_id.as_lot.id})
