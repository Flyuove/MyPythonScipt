# -*- coding: utf-8 -*-
from odoo import http

# class ContractYu(http.Controller):
#     @http.route('/contract_yu/contract_yu/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contract_yu/contract_yu/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('contract_yu.listing', {
#             'root': '/contract_yu/contract_yu',
#             'objects': http.request.env['contract_yu.contract_yu'].search([]),
#         })

#     @http.route('/contract_yu/contract_yu/objects/<model("contract_yu.contract_yu"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contract_yu.object', {
#             'object': obj
#         })