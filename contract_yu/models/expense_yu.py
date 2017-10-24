# -*- coding: utf-8 -*-

from odoo import models, fields, api
import warnings
from decimal import Decimal
import re

class ContractYu(models.Model):
    _inherit = ['hr.expense']

    x_hotel_fees = fields.Float(string="住宿费/对公付款-专票费用")
    x_hotel_normal = fields.Float(string="住宿费普票费用")
    x_car_ship = fields.Float(string="车船费")
    x_city_transportation = fields.Float(string="市内交通费")
    x_tolls = fields.Float(string="过路过桥费")
    x_air_ticket = fields.Float(string="机票费")
    x_subsidy_count = fields.Float(string="补助总额")
    x_start_date = fields.Date(string="出差开始日期")
    x_destination = fields.Char(string="出差地址")
    x_bill_date = fields.Date(string="开票日期-专票")
    x_invoice_code = fields.Char(string="发票代码-10位-专票")
    x_invoice_num = fields.Char(string="发票号码-8位-专票")
    x_invoice_company = fields.Char(string="开票企业-专票")
    x_trip_count = fields.Float(compute='_compute_x_trip_count',string="费用总额",readonly=True)
    x_other_fee = fields.Float(string="其他费用")

    x_contract = fields.Many2one('yu.contract',string="合同") 
    x_financial = fields.Many2one('yu.financial',string="立项")

    x_total_zh = fields.Char(compute='_compute_x_total_zh',string='大写金额',readonly=True)

    @api.depends('x_hotel_fees','x_hotel_normal','x_car_ship','x_city_transportation','x_tolls','x_air_ticket','x_subsidy_count','x_other_fee')
    def _compute_x_trip_count(self):
        for expense in self:
            expense.x_trip_count = expense.x_hotel_fees + expense.x_hotel_normal + expense.x_car_ship + expense.x_city_transportation + expense.x_tolls + expense.x_air_ticket + expense.x_subsidy_count + expense.x_other_fee 


    '''
    人民币数字转大写汉字
    '''
    def cncurrency(self,value):
        #Validate input string
        currencyDigits = str(value)
        if currencyDigits == "":
            return "零元";
        if not re.match('[ ^,.\d]',currencyDigits):
            return "小写金额含有无效字符!"
        if re.match('((\d{1, 3}(, \d{3}) * (.((\d{3}, ) * \d{1, 3}))?) | (\d+(.\d+)?))$',currencyDigits):
            return "小写金额的格式不正确!"
    
        #Normalize the format of input digits:
        currencyDigits,number = re.subn('[,，]|^0+','',currencyDigits)
    
        # 转换为Decimal，并截断多余小数
        if not isinstance(value, Decimal):
            value = Decimal(value).quantize(Decimal('0.01'))
    
        if value == 0:
            return '零元'

        # 处理负数
        prefix = ''
        if value < 0:
            prefix += '负'  # 输出前缀，加负
            value = - value  # 取正数部分，无须过多考虑正负数舍入
    
        #9千亿
        if value > 999999999999.99:
            raise ValueError('\n 亲：你金额太大了，我都不知道该怎么表达。\n ￣▽￣  如此大的金额，还请确认一下是否可以报销 \n 有事请联系：余生华')
    
        integral, decimal = str(value).split('.')  # 小数部分和整数部分分别处理
    
        # 汉字金额字符定义
        dunit = ('角', '分')
        num = ('零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖')
        iunit = ['','拾', '佰', '仟', '万', '拾', '佰', '仟', '亿', '拾', '佰', '仟', '万', '拾', '佰', '仟']
        big = ['','万','亿']
        so = []  # 用于记录转换结果
        so.append(prefix)
        #integral = integral[::-1]  # 翻转整数部分字符串
        if int(integral) > 0:
            zeroCount = 0
            for i,d in enumerate(integral):
                p = len(integral) -i -1
                d = int(d)
                modulus = p % 4
                if d == 0:
                    zeroCount += 1
                else:
                    if zeroCount > 0:
                        so.append(num[0])
                    zeroCount = 0
                    so.append(num[d])
                    so.append(iunit[modulus])
                if p % 4 ==0 and zeroCount < 4:
                    so.append(big[int(p / 4)])
                    zeroCount = 0
            so.append('元')
    
        if int(decimal) > 0:
            for i, d in enumerate(decimal):
                d = int(d)
                if d != 0:
                    so.append(num[d])
                    so.append(dunit[i])
        else:
            so.append('整')
    
    
        return ''.join(so)

    @api.depends('unit_amount')
    def _compute_x_total_zh(self):
        for expense in self:
            expense.x_total_zh = self.cncurrency(expense.unit_amount)

