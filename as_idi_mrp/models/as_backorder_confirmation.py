# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def _process(self, cancel_backorder=False):
        res = super(StockBackorderConfirmation, self)._process()
        for confirmation in self:
            usados = [] 
            for picking_anterior in  confirmation.pick_ids:
                for picking_creado in picking_anterior.backorder_ids:
                    if picking_anterior.picking_type_id.code =='outgoing':
                        for contender in picking_anterior.as_contenedor_id:
                            if not contender.as_entregado:
                                vals = {
                                    "name": contender.name ,
                                    "as_pesob_kg": contender.as_pesob_kg,
                                    "picking_id": picking_creado.id,
                                    "as_peson_kg": contender.as_peson_kg,
                                    "as_pesob_lb": contender.as_pesob_lb,
                                    "as_peson_lb": contender.as_peson_lb,
                                    "as_lote": contender.as_lote.ids,
                                }
                                contenido = self.env['as.contenedor'].create(vals)

        return res

#   for confirmation in self:
#             usados = [] 
#             for picking_anterior in  confirmation.pick_ids:
#                 for pick in picking_anterior:
#                     for contender in pick.as_contenedor_id:
#                         if contender.as_entregado:
#                             for lot in contender.as_lote.ids:
#                                 usados.append(lot)
#                 for picking_creado in picking_anterior.backorder_ids:
#                     for contender in picking_anterior.as_contenedor_id:
#                         ausar = [] 
#                         for lote in contender.as_lote:
#                             if lote.id not in usados:
#                                 ausar.append(lote.id)
#                         if ausar != []:
#                             vals = {
#                                 "name": contender.name ,
#                                 "as_pesob_kg": contender.as_pesob_kg,
#                                 "picking_id": picking_creado.id,
#                                 "as_peson_kg": contender.as_peson_kg,
#                                 "as_pesob_lb": contender.as_pesob_lb,
#                                 "as_peson_lb": contender.as_peson_lb,
#                                 "as_lote": ausar,
#                             }
#                             contenido = self.env['as.contenedor'].create(vals)

                                

#         return res
