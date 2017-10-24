# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FinancialYu(models.Model):
    _name = 'yu.financial'

    name = fields.Char(string="立项标题",required=True)
    code = fields.Char(string="立项编号",required=True,index=True)
    amount = fields.Float(string="立项金额",required=True)
    description = fields.Text(string="说明")

    user_id = fields.Many2one('res.users',string="拟稿人",required=True, default=lambda self: self.env.user)
