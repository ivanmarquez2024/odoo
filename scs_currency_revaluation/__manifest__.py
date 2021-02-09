# See LICENSE file for full copyright and licensing details.

{
    'name': 'Multi Currency RE-Evaluation Unrealized Gain Loss',
    'version': '13.0.1.0.0',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': """When you run the RE-Evaluation process,
the balance in each main account posted in a foreign currency will be revalued.
The unrealized gain or loss transactions that are created during
the RE-Evaluation process are system-generated.
""",
    'description': """When you run the RE-Evaluation process,
the balance in each main account posted in a foreign currency will be revalued.
The unrealized gain or loss transactions that are created during
the RE-Evaluation process are system-generated.
""",
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'depends': ['account'],
    'data': [
             'data/forex_invoice_entry_schedular.xml',
             'views/company_view.xml',
             'views/account_move_view.xml'
            ],
    'images': ['static/description/img/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 99,
    'currency': 'EUR',
}
