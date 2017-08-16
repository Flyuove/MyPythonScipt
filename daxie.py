# -*- coding: utf-8 -*-

'''
人民币数字转大写汉字
'''
import warnings
from decimal import Decimal
import re


def cncurrency(value):
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


i=input('请输入金额：')
print (cncurrency(i))

