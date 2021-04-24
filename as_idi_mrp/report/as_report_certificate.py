# # -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime
from odoo import api, models, _
from odoo.exceptions import UserError
from io import BytesIO
from urllib.request import urlopen
from odoo.tools.image import image_data_uri
from odoo.exceptions import UserError
from odoo.exceptions import Warning

class as_kardex_productos_excel(models.AbstractModel):
    _name = 'report.as_idi_mrp.report_certificate_idi.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):        
        dict_almacen = []
        dict_aux = []
        lotes= []
        filtro = ''
        #restriccion de productos distintos en un mismo reporte
        product_id =  lines[0].product_id
        mo_id =  lines[0]
        generate = True
        for line in lines:
            lotes.append(line.as_lot.id)
            if product_id != line.product_id:
                generate=False
            
        # if data['form']['stage_id']:
        #     filtro+= ' and hs.id in '+ str(data['form']['stage_id']).replace('[','(').replace(']',')')
        # if data['form']['partner_id']:
        #     filtro+= ' and rp.id in '+ str(data['form']['partner_id']).replace('[','(').replace(']',')')
        # if data['form']['as_empresa']:
        #     filtro+= ' and ae.id in '+ str(data['form']['as_empresa']).replace('[','(').replace(']',')')
        sheet = workbook.add_worksheet('Detalle de Movimientos')
        sheet.set_paper(1)  
        # sheet.center_horizontally()
        
        sheet.set_landscape()
        #worksheet.center_horizontally()
        
        titulo1 = workbook.add_format({'font_size': 16, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'bold':True })
        titulo2 = workbook.add_format({'font_size': 14, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        titulo3 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True })
        titulo3_number = workbook.add_format({'font_size': 14, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 12, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True})

        number_left = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00'})
        number_perosonalizado = workbook.add_format({'font_size': 12, 'align': 'center', 'num_format': 0})
        number_right = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00'})
        number_right_bold = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'bold':True})
        number_right_col = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
        number_center = workbook.add_format({'font_size': 12, 'align': 'center', 'num_format': '#,##0.00'})
        number_right_col.set_locked(False)
        numero_personalizado = workbook.add_format({'font_size': 12, 'align': 'center','valign': 'vcenter','text_wrap': True,'bottom': True, 'top': True, 'left': True, 'right': True})

        letter12 = workbook.add_format({'font_size': 12, 'align': 'center', 'text_wrap': True, 'bold':True,'bottom': True, 'top': True, 'left': True, 'right': True})
        letter11 = workbook.add_format({'font_size': 12, 'align': 'center', 'valign': 'vcenter','text_wrap': True,'bottom': True, 'top': True, 'left': True, 'right': True})
        letter1 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True})
        letter1d = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True})
        letter2 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold':False})
        letter3 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True})
        letter4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter5 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True, 'bold': True})
        letter_locked = letter3
        letter_locked.set_locked(False)

        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',4, letter1)
        sheet.set_column('B:B',15, letter1)
        sheet.set_column('C:C',15, letter1)
        sheet.set_column('D:D',10, letter1)
        sheet.set_column('E:E',10, letter1)
        sheet.set_column('F:F',10, letter1)
        sheet.set_column('G:G',10, letter1)
        sheet.set_column('H:H',10, letter1)
        sheet.set_column('I:I',10, letter1)
        sheet.set_column('J:J',20, letter1)
        sheet.set_column('K:K',10, letter1)
        

        sheet.set_row(9,35)
        sheet.set_row(10,15)

        code_format = product_id.as_format_type_id.as_code

        if code_format == 3:
            sheet.set_row(17,30)
            sheet.set_print_scale(61)
        if code_format == 4:
            sheet.set_row(19,30)
            sheet.set_print_scale(51)

        if code_format == 1:
            columnas = product_id.as_format_type_id.as_cant_column
            sheet.set_print_scale(70)
        if code_format == 2:
            columnas = product_id.as_format_type_id.as_cant_column
            sheet.set_print_scale(60)
        else:
            columnas = product_id.as_format_type_id.as_cant_column
        if not generate or not product_id.as_format_type_id:
            sheet.merge_range(2,5,3,15,'No se puedo generar el reporte los productos son distintos o producto no posee formato establecido',titulo1) 
        elif generate:
            if code_format == 2:
                sheet.merge_range(1,8,2,11,'BMC Certificate Of Analysis',titulo1) 
                # sheet.set_row(17,30)
            elif code_format == 1:
                sheet.merge_range(1,6,2,9,'BMC Certificate Of Analysis',titulo1) 
                # sheet.set_row(17,30)
            elif code_format == 3:
                sheet.merge_range(1,7,2,9,'SMC Certificate Of Analysis',titulo1) 
                # sheet.set_row(17,30)
            else:
                sheet.merge_range(1,9,2,11,'SMC Certificate Of Analysis',titulo1) 
                # sheet.set_row(19,30)
            # fecha_inicial = datetime.strptime(data['form']['start_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
            # fecha_final = datetime.strptime(data['form']['end_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
            # # Titulos, subtitulos, filtros y campos del reporte.
            url = image_data_uri(self.env.user.company_id.logo)
            image_data = BytesIO(urlopen(url).read())
            sheet.insert_image('B1', url, {'image_data': image_data,'x_scale': 0.4, 'y_scale': 0.3})      
            fecha = (datetime.now()- timedelta(hours=5)).strftime('%d/%m/%Y %H:%M:%S')
            customer = ''
            if mo_id:
                customer=mo_id.as_sale.partner_id.name
            sheet.write(4, 1, 'Material: ',letter1) 
            sheet.write(4, 2, product_id.name,letter2)         
            sheet.write(5, 1, 'Color: ',letter1) 
            sheet.write(5, 2, product_id.as_color,letter2) 
            sheet.write(6, 1, 'Customer: ',letter1) 
            sheet.write(6, 2, customer,letter2)         
            sheet.write(7, 1, 'Commercial Guarantee: ',letter1) 
            sheet.write(7, 2, product_id.product_tmpl_id.x_studio_guarantee,letter2) 

            # sheet.merge_range('A2:D2', 'Dirección: '+self.env.user.company_id.street, letter1)
            # sheet.merge_range('A3:D3', 'Telefono: '+self.env.user.company_id.phone, letter1)
            # sheet.merge_range('A4:D4', str(self.env.user.company_id.city)+'-'+str(self.env.user.company_id.country_id.name))
            # sheet.merge_range('F1:I1', 'Usuario Impresión: '+self.env.user.name, letter1)
            # sheet.merge_range('F2:I2', 'Fecha y Hora Impresión: '+fecha, letter1)
            
            #sheet.merge_range('A5:I5', 'REPORTE DE TICKETS SOPORTE', titulo1)
            #sheet.set_row(7, 40)
            #sheet.merge_range('A6:I6', 'DEL '+fecha_inicial+' AL '+fecha_final, letter11)
            filas = 8
            filas += 1
            point_array =[]
            point_all = self.env['quality.point'].search([('product_tmpl_id', '=', product_id.product_tmpl_id.id)],order='as_secuencia asc',limit=columnas)
            quality_check_all = self.env['quality.check'].search([('lot_id', '=', tuple(lotes))])
            #check_one= quality_check_all[0]
            for quelity in quality_check_all:
                for point in point_all:
                    if quelity.point_id.id == point.id:
                        point_array.append(point.id)
            # if columnas > 6:
            #     sheet.set_print_scale(53)
            # if columnas >= 8:
            #     sheet.set_print_scale(50)
            # if columnas >= 9:
            #     sheet.set_print_scale(47)
            # if columnas >= 10:
            #     sheet.set_print_scale(44)
            # if columnas >= 11:
            #     sheet.set_print_scale(41)
            # if columnas >= 12:
            #     sheet.set_print_scale(38)
            point = self.env['quality.point'].search([('id', 'in', point_array)],order='as_secuencia asc',limit=columnas)
            quality_check = self.env['quality.check'].search([('product_id', '=', product_id.id)])
            if code_format == 3:
                sheet.merge_range('B10:E10', 'Propierty', letter12)
                sheet.merge_range('F10:I10', 'Unit', letter12)
                sheet.merge_range('J10:M10', 'Specification', letter12)
                sheet.merge_range('N10:R10', 'Reference Method', letter12)
                filas += 1
                cont=10
                for item in point_all:
                    cont +=1
                    sheet.merge_range('B'+str(cont)+':E'+str(cont), str(item.title), letter11)
                    sheet.merge_range('F'+str(cont)+':I'+str(cont), str(item.norm_unit), letter11)
                    sheet.merge_range('J'+str(cont)+':M'+str(cont), str(item.tolerance_min)+'-'+str(item.tolerance_max), letter11)
                    sheet.merge_range('N'+str(cont)+':R'+str(cont),item.x_studio_mtodo, letter11)
                    #sheet.write(cont-1,15, item.x_studio_mtodo, letter11)
                    filas += 1
            if code_format >= 4:
                sheet.merge_range('B10:F10', 'Propierty', letter12)
                sheet.merge_range('G10:J10', 'Unit', letter12)
                sheet.merge_range('K10:P10', 'Specification', letter12)
                sheet.merge_range('Q10:V10', 'Reference Method', letter12)
                filas += 1
                cont=10
                for item in point_all:
                    cont +=1
                    sheet.merge_range('B'+str(cont)+':F'+str(cont), str(item.title), letter11)
                    sheet.merge_range('G'+str(cont)+':J'+str(cont), str(item.norm_unit), letter11)
                    sheet.merge_range('K'+str(cont)+':P'+str(cont), str(item.tolerance_min)+'-'+str(item.tolerance_max), letter11)
                    sheet.merge_range('Q'+str(cont)+':V'+str(cont),item.x_studio_mtodo, letter11)
                    #sheet.write(cont-1,15, item.x_studio_mtodo, letter11)
                    filas += 1
            if int(code_format) >= 3:
                filas = cont
                filas += 1
                sheet.write(filas, 1, '#Batch',letter12) #cliente/proveedor
                sheet.merge_range(filas, 2,filas,3, 'Manufacturing Date',letter12) #cliente/proveedor
                sheet.merge_range(filas, 4,filas,5, '#Box',letter12) #cliente/proveedor
                cont =6
                for intem in point:
                    sheet.merge_range(filas, cont,filas,cont+1, intem.title+'('+intem.norm_unit+') ',letter12) #cliente/proveedor   
                    cont+=2
                filas += 1
                for check in lines:
                    quality_check = self.env['quality.check'].search([('lot_id', '=', check.as_lot.id)])
                    dia = datetime.strptime(str(check.date_planned_start), '%Y-%m-%d %H:%M:%S').strftime('%d')
                    mes = datetime.strptime(str(check.date_planned_start), '%Y-%m-%d %H:%M:%S').strftime('%m')
                    year = datetime.strptime(str(check.date_planned_start), '%Y-%m-%d %H:%M:%S').strftime('%Y')
                    fecha = str(dia)+'/'+str(self.get_mes(mes))+'/'+year
                    lote= ''
                    if check.as_lot:
                        lote = check.as_lot.name
                    sheet.write(filas, 1,lote,numero_personalizado) 
                    sheet.merge_range(filas, 2,filas, 3,fecha,numero_personalizado) 
                    caja=''
                    if quality_check:

                        # box = self.env['as.contenedor'].search([('as_lote', 'in', [check.as_lot.id])])
                        # # box_aux = self.env['quality.check'].search([('point_id', '=',intem.id)])
                        # for linea in box:
                        #     caja = linea.name
                        for aux in quality_check:
                            box_aux = self.env['quality.check'].search([('id', '=',aux.id)])
                            if box_aux.as_box:
                                caja = box_aux.as_box

                    sheet.merge_range(filas, 4,filas,5,caja,numero_personalizado) 
                    cont =6
                    for intem in point:
                        qa_check_aux = self.env['quality.check'].search([('point_id', '=',intem.id)])
                        value = 0.0
                        decimales = 0
                        decimales_num = 0
                        formato = '{:,.'
                        for item in quality_check:
                            if intem.id == item.point_id.id:
                                value = item.measure
                                if item.as_decimales == False:
                                    decimales = '0'
                                else:
                                    decimales = item.as_decimales
                        if intem.as_decimales_num == False:
                            decimales_num = '0'
                        else:
                            decimales_num = intem.as_decimales_num
                        formato +=  decimales_num 
                        formato += 'f}'
                        sheet.merge_range(filas, cont,filas, cont+1, formato.format(value),numero_personalizado) #cliente/proveedor   
                        cont+=2
                    filas += 1
            else:
                sheet.merge_range(filas,1,filas+2,1,'Batch',letter11)
                sheet.merge_range(filas,2,filas+2,2,'Manufacturing Date',letter11)
                # sheet.merge_range(8,3,8,5,'hola1',letter12) #cliente/proveedor   
                # sheet.merge_range(8,6,8,8,'hola2',letter12) #cliente/proveedor   
                # sheet.merge_range(9,3,9,5,'hola3',letter12) #cliente/proveedor   

                cont =3
                for intem in point:
                    sheet.merge_range(filas,cont,filas,cont+2,str(intem.title)+'('+str(intem.norm_unit)+') '+str(intem.x_studio_mtodo),letter11)
                    sheet.merge_range(filas+1,cont,filas+1,cont+1,'Specification',letter11)
                    sheet.merge_range(filas+1,cont+2,filas+2,cont+2,'Result',letter11)
                    sheet.write(filas+2, cont, 'Min',letter11) #cliente/proveedor
                    sheet.write(filas+2, cont+1, 'Max',letter11) #cliente/proveedor
                    cont+=3
                filas += 3
                for check in lines:
                    quality_check = self.env['quality.check'].search([('lot_id', '=', check.as_lot.id)])
                    dia = datetime.strptime(str(check.date_planned_start), '%Y-%m-%d %H:%M:%S').strftime('%d')
                    mes = datetime.strptime(str(check.date_planned_start), '%Y-%m-%d %H:%M:%S').strftime('%m')
                    year = datetime.strptime(str(check.date_planned_start), '%Y-%m-%d %H:%M:%S').strftime('%Y')
                    fecha = str(dia)+'/'+str(self.get_mes(mes))+'/'+year
                    sheet.write(filas, 1,check.as_lot.name,letter11) 
                    sheet.write(filas, 2,fecha,letter11) 
                    cont =3
                    for intem in point:
                        value = 0
                        decimales = 0
                        formato = '{:.'
                        for item in quality_check:
                            if intem.id == item.point_id.id:
                                value = item.measure
                                if item.as_decimales == False:
                                    decimales = '0'
                                else:
                                    decimales = item.as_decimales
                        ## Decimales quality point
                        if intem.as_decimales_num == False:
                            decimales = '0'
                        else:
                            decimales = intem.as_decimales_num
                        formato +=  decimales
                        formato += 'f}'
                        #sheet.write(filas, cont, float(intem.tolerance_min),numero_personalizado) #cliente/proveedor   
                        sheet.write(filas, cont, formato.format(intem.tolerance_min),numero_personalizado) #cliente/proveedor   
                        cont+=1                
                        #sheet.write(filas, cont, float(intem.tolerance_max),numero_personalizado) #cliente/proveedor   
                        sheet.write(filas, cont, formato.format(intem.tolerance_max),numero_personalizado) #cliente/proveedor   
                        cont+=1                
                        #sheet.write(filas, cont, float(value),numero_personalizado) #cliente/proveedor   
                        sheet.write(filas, cont, formato.format(value),numero_personalizado) #cliente/proveedor   
                        cont+=1
                    filas += 1
            filas += 2

            if code_format == 1:
                sheet.merge_range(filas,1,filas+6,14,product_id.as_format_type_id.as_slogan,letter1) #cliente/proveedor 
                filas += 8
                ###Definir donde se rendea el pie slogan con los datos de la empresa
                sheet.merge_range(filas,9,filas+3,6,product_id.as_format_type_id.as_sfooter,letter1d) 
                ###FIN
                url = image_data_uri(product_id.as_format_type_id.image)
                image_data = BytesIO(urlopen(url).read())
                #Agregar la IMAGEN en posicion N y filas + 1
                sheet.insert_image('N'+str(filas+1), url, {'image_data': image_data,'x_offset': 0.7, 'y_offset': 0.5}) 
                sheet.merge_range(filas+3,14,filas+3,12,product_id.as_format_type_id.as_code_iso,letter1) 

            elif code_format == 3:
                sheet.merge_range(filas,1,filas+6,17,product_id.as_format_type_id.as_slogan,letter1) #cliente/proveedor 
                filas += 8
                ###Definir donde se rendea el pie slogan con los datos de la empresa
                sheet.merge_range(filas,10,filas+3,7,product_id.as_format_type_id.as_sfooter,letter1d) 
                ###FIN
                url = image_data_uri(product_id.as_format_type_id.image)
                image_data = BytesIO(urlopen(url).read())
                #Agregar la IMAGEN en posicion N y filas + 1
                sheet.insert_image('Q'+str(filas+1), url, {'image_data': image_data,'x_offset': 0.7, 'y_offset': 0.5}) 
                sheet.merge_range(filas+3,17,filas+3,15,product_id.as_format_type_id.as_code_iso,letter1) 
            
            elif code_format >= 4:
                sheet.merge_range(filas,1,filas+6,21,product_id.as_format_type_id.as_slogan,letter1) #cliente/proveedor 
                filas += 8
                ###Definir donde se rendea el pie slogan con los datos de la empresa
                sheet.merge_range(filas,12,filas+3,9,product_id.as_format_type_id.as_sfooter,letter1d) 
                ###FIN
                url = image_data_uri(product_id.as_format_type_id.image)
                image_data = BytesIO(urlopen(url).read())
                #Agregar la IMAGEN en posicion N y filas + 1
                sheet.insert_image('U'+str(filas+1), url, {'image_data': image_data,'x_offset': 0.7, 'y_offset': 0.5}) 
                sheet.merge_range(filas+3,21,filas+3,19,product_id.as_format_type_id.as_code_iso,letter1) 

            else:
                sheet.merge_range(filas,1,filas+6,17,product_id.as_format_type_id.as_slogan,letter1) #cliente/proveedor 
                filas += 8
                ###Definir donde se rendea el pie slogan con los datos de la empresa
                sheet.merge_range(filas,11,filas+3,8,product_id.as_format_type_id.as_sfooter,letter1d) 
                ###FIN
                url = image_data_uri(product_id.as_format_type_id.image)
                image_data = BytesIO(urlopen(url).read())
                #Agregar la IMAGEN en posicion N y filas + 1
                sheet.insert_image('Q'+str(filas+1), url, {'image_data': image_data,'x_offset': 0.7, 'y_offset': 0.5}) 
                sheet.merge_range(filas+3,17,filas+3,15,product_id.as_format_type_id.as_code_iso,letter1) 

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