# -*- coding: utf-8 -*-
{
    'name' : "Ahorasoft MRP customizaciones",
    'version' : "1.1.5",
    'author'  : "Ahorasoft",
    'description': """
Customizaciones para IDI
===========================

Custom module for Latproject
    """,
    'category' : "MRP",
    'depends' : ["mrp","product",'sale','purchase','stock','report_xlsx','uom'],
    'website': 'http://www.ahorasoft.com',
    'data' : [
        'security/ir.model.access.csv',
        'views/as_mrp_production.xml',
        'views/as_machine.xml',
        'views/as_product_category.xml',
        'wizard/mrp_product_produce.xml',
        'views/as_sale_order.xml',
        'views/as_stock_picking.xml',
        'views/as_contenedor.xml',
        'views/as_product_template.xml',
        'views/as_res_partner.xml',
        'views/as_report_format.xml',
        'views/as_quality_views.xml',
        'views/as_stock_move_line.xml',
        'report/as_empaque_report.xml',
        'wizard/as_programa_produccion.xml',
        'wizard/as_ordenes_pendientes.xml',
        'report/as_report_materia_prima.xml',
        'data/update_mo_cron.xml',
             ],
    'demo' : [],
    'installable': True,
    'auto_install': False
}
