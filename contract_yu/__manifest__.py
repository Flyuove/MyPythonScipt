# -*- coding: utf-8 -*-
{
    'name': "contract_yu",

    'summary': "contract pice",

    'description': "some contract expense",

    'author': "steam yu",
    'website': "http://www.cool-srv.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_expense'],

    'data': [
        'security/ir.model.access.csv',
        'views/contract_yu.xml',
        'views/financial_establishment.xml',
        'views/expense_yu.xml',
        'views/templates.xml',
        'report/report_hr_holidays.xml',
        'views/holidays_yu.xml'
    ],
}
