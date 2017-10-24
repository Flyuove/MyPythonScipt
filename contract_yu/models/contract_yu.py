# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ContractYu(models.Model):
    _name = 'yu.contract'

    name = fields.Char(string="合同名称",required=True)
    code = fields.Char(string="合同编号",required=True,index=True)
    vendor = fields.Many2one('res.partner',string="供应商",domain=[('supplier','=',1), ('parent_id', '=', False)])
    description = fields.Text(string="说明")

    startDate = fields.Date(string="合同起始日",default=fields.Date.today)
    endDate = fields.Date(string="合同终止日",default=fields.Date.today)
    user_id = fields.Many2one('res.users',string="合同持有人",required=True,default=lambda self: self.env.user)
    type = fields.Selection([(1,'纸质+扫描件'),(2,'扫描件')],default=1,string='合同形式')
