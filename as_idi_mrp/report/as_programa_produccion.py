# # -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime
import odoo.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta
import datetime
from datetime import datetime, timedelta, date

class as_kardex_productos_excel(models.AbstractModel):
    _name = 'report.as_idi_mrp.master_program.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):   
            dict_almacen = []
            dict_aux = []
            # if data['form']['as_almacen']:
            #     for line in data['form']['as_almacen']:
            #         dict_almacen.append('('+str(line)+')')
            #         dict_aux.append(line)
            # else:
            #     almacenes_internos = self.env['stock.location'].search([('usage', '=', 'internal')])
            #     for line in almacenes_internos:
            #         dict_almacen.append('('+str(line.id)+')')
            #         dict_aux.append(line.id)
    
            #Definiciones generales del archivo, formatos, titulos, hojas de trabajo
            sheet = workbook.add_worksheet('Detalle de Movimientos')
            titulo1 = workbook.add_format({'font_size': 16, 'align': 'center', 'text_wrap': True, 'bold':True })
            titulo2 = workbook.add_format({'font_size': 13, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
            titulo3 = workbook.add_format({'font_size': 11, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
            titulo3_number = workbook.add_format({'font_size': 13, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
            titulo4 = workbook.add_format({'font_size': 13, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':True })
            titulo5 = workbook.add_format({'font_size': 13, 'align': 'left', 'text_wrap': True, 'bold':True })

            number_left = workbook.add_format({'font_size': 11, 'align': 'left', 'num_format': '#,##0.00'})
            number_right = workbook.add_format({'font_size': 11, 'align': 'right', 'num_format': '#,##0.00'})
            number_right_bold = workbook.add_format({'font_size': 11, 'align': 'right', 'num_format': '#,##0.00', 'bold':True})
            number_right_col = workbook.add_format({'font_size': 11, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
            number_center = workbook.add_format({'font_size': 11, 'align': 'center', 'num_format': '#,##0.00'})
            number_right_col.set_locked(False)

            letter1 = workbook.add_format({'font_size': 11, 'align': 'left', 'text_wrap': True})
            letter1c = workbook.add_format({'font_size': 11, 'align': 'left', 'text_wrap': True,'color': 'red'})
            letter2 = workbook.add_format({'font_size': 11, 'align': 'left', 'bold':True})
            letter3 = workbook.add_format({'font_size': 11, 'align': 'right', 'text_wrap': True})
            letter4 = workbook.add_format({'font_size': 11, 'align': 'left', 'text_wrap': True, 'bold': True})
            letter5 = workbook.add_format({'font_size': 11, 'align': 'right', 'text_wrap': True, 'bold': True})
            letter_locked = letter3
            letter_locked.set_locked(False)

            # Aqui definimos en los anchos de columna
            sheet.set_column('A:A',15, letter1)
            sheet.set_column('B:B',30, letter1)
            sheet.set_column('C:C',15, letter1)
            sheet.set_column('D:D',18, letter1)
            sheet.set_column('E:E',15, letter1)
            sheet.set_column('F:F',15, letter1)
            sheet.set_column('G:G',15, letter1)
            sheet.set_column('H:H',15, letter1)
            sheet.set_column('I:I',15, letter1)
            sheet.set_column('J:J',15, letter1)
            sheet.set_column('K:K',15, letter1)
            sheet.set_column('L:L',15, letter1)
            sheet.set_column('N:N',15, letter1)
            sheet.set_column('O:O',15, letter1)
            sheet.set_column('M:M',15, letter1)
            sheet.merge_range('A1:G1', 'NOMBRE O RAZON SOCIAL:'+str(self.env.user.company_id.name), titulo5)
            sheet.merge_range('A2:D2', 'NIT: '+str(self.env.user.company_id.vat), titulo5)
            sheet.merge_range('A3:D3', 'Email: '+str(self.env.user.company_id.email)+' Teléfono: '+str(self.env.user.company_id.phone), titulo5)
            sheet.merge_range('A4:D4', str(self.env.user.company_id.city)+' '+str(self.env.user.company_id.country_id.name), titulo5)

            # Titulos, subtitulos, filtros y campos del reporte
            sheet.merge_range('A5:G5', 'REPORTE DE BAJO STOCK', titulo1)
            fecha = (datetime.now()- timedelta(hours=5)).strftime('%d/%m/%Y %H:%M:%S')
            # fecha_inicial = datetime.strptime(data['form']['start_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
            # fecha_final = datetime.strptime(data['form']['end_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
            # sheet.write(5, 0, 'Fechas: ', letter4)
            # sheet.merge_range('B6:D6', fecha_inicial +' - '+ fecha_final)
            # sheet.write(6, 0, 'Estacion: ', letter4)
            # sheet.write(6, 3, 'Producto: ', letter4)
            # filtro_almacenes_name = 'VARIOS'
            # product = self.env['product.template'].search([('id', '=', data['form']['as_productos'])], limit=1)
            # for y in dict_aux:
            #     almacen_obj = self.env['stock.location'].search([('id', '=', y)], limit=1)
            #     filtro_almacenes_name += ', '+almacen_obj.name
            # sheet.merge_range('B7:C7', filtro_almacenes_name)
            # sheet.merge_range('E7:G7', product.name)
            sheet.merge_range('E7:F7', 'Fecha impresion: ', letter5)
            sheet.merge_range('G7:H7', fecha)

            sheet.write(7, 0, 'ITEM', titulo2)
            sheet.write(7, 1, 'CODE', titulo2)
            sheet.write(7, 2, 'ON HAND', titulo2)
            sheet.write(7, 3, 'UDM', titulo2)
            sheet.write(7, 4, 'DUE DATE', titulo2)
            sheet.write(7, 5, 'QTY REQUERED', titulo2)
            sheet.write(7, 6, 'BALANCE', titulo2)
            filas = 8
            sheet.freeze_panes(8, 0)
            query_movements = ("""
                    select 
                    pt.id,
                    pt.name,
                    pt.default_code,
                    mpf.date,
                    mpf.replenish_qty,
                    mps.id
                    from mrp_production_schedule mps
                    join mrp_product_forecast mpf on mps.id = mpf.production_schedule_id
                    join product_product pp on pp.id = mps.product_id
                    join product_template pt on pp.product_tmpl_id = pt.id
                    order by pt.name,mpf.date
                    """)
            #_logger.debug(query_movements)
            self.env.cr.execute(query_movements)
            all_movimientos_almacen = [k for k in self.env.cr.fetchall()]
            movimientos_almacen = []
            
            for line in all_movimientos_almacen:
                value_qty = 0.0
                product = self.env['product.template'].search([('id', '=', line[0])], limit=1)
                if product.name:
                    msp = self.env['mrp.production.schedule'].search([('id', '=', line[5])], limit=1).get_production_schedule_view_state()
                    for value in msp[0]['forecast_ids']:
                        if str(line[3])== str(value['date_stop']):
                            value_qty = value['replenish_qty']
                    if value_qty:
                        qty = float(product.qty_available)-value_qty
                    else:
                        qty = float(product.qty_available)
                    if qty > 0:
                        formato = letter1
                    else:
                        formato = letter1c

                    fecha_inv =  (datetime.strptime(str(line[3]), '%Y-%m-%d') + relativedelta(days=5)).strftime('%d/%m/%Y')
                    sheet.write(filas,0,product.name,formato)
                    sheet.write(filas,1,product.default_code or '',formato)
                    sheet.write(filas,2,product.qty_available or 0,formato)
                    sheet.write(filas,3,product.uom_id.name or '',formato)
                    sheet.write(filas,4,fecha_inv,formato)
                    sheet.write(filas,5,value_qty or '',formato)
                    sheet.write(filas,6,qty or 0,formato)
                    filas += 1


