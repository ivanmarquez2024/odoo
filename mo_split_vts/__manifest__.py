{
    'name': 'Dividir ordenes de Produccion',
    'version': '1.0.8',
    'category': 'Manufacturing',
    'author': "Ahorasoft",
    'price': 27
,
    'currency': 'BOB',
    'summary':"This Module Allow us to Dividir ordenes de ProduccionBased on Number of Split.Split Mo in Equal Part",
    'depends': [
        'mrp','as_idi_mrp'
    ],
    'data': [
        'views/mo_split_view.xml',
        'views/mrp_production.xml',
        'wizard/res_config.xml',
    ],
    'qweb': [],
    'css': [],
    'js': [],
    'images': [
        'static/description/split_mo_wizard.png',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}
