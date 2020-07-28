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
    _name = 'report.as_idi_mrp.ordenes_pendientes.xlsx'
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
            titulo2l = workbook.add_format({'font_size': 13, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True,'bg_color': 'silver'})
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
            formatol = workbook.add_format({'font_size': 11, 'align': 'center','bg_color': 'silver'})
            formato = workbook.add_format({'font_size': 11, 'align': 'center', 'bold':False})
            formatof = workbook.add_format({'font_size': 11, 'align': 'left', 'bold':False})
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
            sheet.set_column('B:B',15, letter1)
            sheet.set_column('C:C',15, letter1)
            sheet.set_column('D:D',30, letter1)
            sheet.set_column('E:E',15, letter1)
            sheet.set_column('F:F',40, letter1)
            sheet.set_column('G:G',15, letter1)
            sheet.set_column('H:H',15, letter1)
            sheet.set_column('I:I',15, letter1)
            sheet.set_column('J:J',15, letter1)
            sheet.set_column('K:K',15, letter1)
            sheet.set_column('L:L',15, letter1)
            sheet.set_column('N:N',15, letter1)
            sheet.set_column('O:O',15, letter1)
            sheet.set_column('M:M',18, letter1)
            sheet.merge_range('A1:G1', 'NOMBRE O RAZON SOCIAL:'+str(self.env.user.company_id.name), titulo5)
            sheet.merge_range('A2:D2', 'NIT: '+str(self.env.user.company_id.vat), titulo5)
            sheet.merge_range('A3:D3', 'Email: '+str(self.env.user.company_id.email)+' Teléfono: '+str(self.env.user.company_id.phone), titulo5)
            sheet.merge_range('A4:D4', str(self.env.user.company_id.city)+' '+str(self.env.user.company_id.country_id.name), titulo5)

            # Titulos, subtitulos, filtros y campos del reporte
            sheet.merge_range('A5:G5', 'REPORTE DE ORDENES POR ENTREGAR', titulo1)
            fecha = (datetime.now()- timedelta(hours=5)).strftime('%d/%m/%Y %H:%M:%S')
            sheet.merge_range('E7:F7', 'Fecha impresion: ', letter5)
            sheet.merge_range('G7:H7', fecha)

            sheet.write(7, 0,'FECHA PO',titulo2)
            sheet.write(7, 1,'PO',titulo2)
            sheet.write(7, 2,'REVISIÓN PO',titulo2l)
            sheet.write(7, 3,'PRODUCTO',titulo2)
            sheet.write(7, 4,'CANT (KG)',titulo2)
            sheet.write(7, 5,'CLIENTE ',titulo2)
            sheet.write(7, 6,'SO',titulo2)
            sheet.write(7, 7,'FECHA DESEADA',titulo2)
            sheet.write(7, 8,'FECHA DE CONFIRMACIÓN',titulo2l)
            sheet.write(7, 9,'CONFIRMACION DE PRODUCCIÓN',titulo2)
            sheet.write(7, 10,'CONFIRMACÓN DE CLIENTE',titulo2l)
            sheet.write(7, 11,'FECHA DE ENTREGA',titulo2)
            sheet.write(7, 12,'MOTIVO',titulo2l)
            sheet.write(7, 13,'DOCUMENTOS',titulo2l)
            filas = 8
            sheet.freeze_panes(8, 0)
            query_movements = ("""
                select 
                so.id
                ,sol.product_uom_qty
                ,rp.name
                ,so.name
                ,so.date_order
                ,so.as_order_partner
                ,pt.name
                ,pp.default_code
                from sale_order so
                join sale_order_line sol on sol.order_id=so.id
                join res_partner rp on so.partner_id=rp.id
                join product_product pp on pp.id = sol.product_id
                join product_template pt on pt.id=pp.product_tmpl_id
                where
                so.state in ('sale','done') and 
                so.date_order::date >='"""+str(data['form']['start_date'])+"""' AND  so.date_order::date <='"""+str(data['form']['end_date'])+"""' 
                group by 1,2,3,4,5,6,7,8
                    """)
            #_logger.debug(query_movements)
            self.env.cr.execute(query_movements)
            all_movimientos_almacen = [k for k in self.env.cr.fetchall()]
            movimientos_almacen = []
            
            for line in all_movimientos_almacen:
                mrp = self.env['mrp.production'].search([('as_sale', '=', line[0])],order='create_date desc',limit=1)
                picking = self.env['stock.picking'].search([('origin', '=', line[2])],order='create_date desc',limit=1)
                fecha1 = ''
                fecha2 = ''
                if 'x_studio_fecha_de_confirmacin' in mrp:
                    fecha1 = mrp.x_studio_fecha_de_confirmacin                
                if 'x_studio_fecha_de_confirmacin_cliente' in mrp:
                    fecha2 = mrp.x_studio_fecha_de_confirmacin_cliente
                sheet.write(filas,0, self.get_format_date(line[4]),formato)
                sheet.write(filas,1, line[5],formato)
                sheet.write(filas,2, '',formatol)
                sheet.write(filas,3, line[6],formatof)
                sheet.write(filas,4, line[1],formato)
                sheet.write(filas,5, line[2] or '',formatof)
                sheet.write(filas,6, line[3] or '',formato)
                sheet.write(filas,7, self.get_format_date(picking.scheduled_date) or '',formato)
                sheet.write(filas,8, self.get_format_date_small(fecha1),formatol)
                sheet.write(filas,9, self.get_format_date_small(fecha2) or '',formato)
                sheet.write(filas,10, '',formatol)
                sheet.write(filas,11, self.get_format_date(picking.date_done),formato)
                sheet.write(filas,12, '',formatol)
                sheet.write(filas,13, '',formatol)
                filas += 1

    def get_format_date(self,date):
        fecha = ''
        if date:
            dia = datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S').strftime('%d')
            mes = self.get_mes(datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S').strftime('%m'))
            year = datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S').strftime('%y')
            fecha= dia+'-'+mes+'-'+year
        return fecha

    def get_format_date_small(self,date):
        fecha = ''
        if date:
            dia = datetime.strptime(str(date), '%Y-%m-%d').strftime('%d')
            mes = self.get_mes(datetime.strptime(str(date), '%Y-%m-%d').strftime('%m'))
            year = datetime.strptime(str(date), '%Y-%m-%d').strftime('%y')
            fecha= dia+'-'+mes+'-'+year
        return fecha

    def get_mes(self,mes):
        mesesDic = {
            "01":'Ene',
            "02":'Feb',
            "03":'Mar',
            "04":'Abr',
            "05":'May',
            "06":'Jun',
            "07":'Jul',
            "08":'Ago',
            "09":'Sep',
            "10":'Oct',
            "11":'Nov',
            "12":'Dic',
        }
        return mesesDic[str(mes)]