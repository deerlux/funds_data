#!/usr/bin/python
# -*- coding: utf8 -*-
import lxml.html
from datetime import datetime
import itertools
import requests

if __name__ == "__main__":
    response = requests.get('http://www.ourku.com/ccmx/630011/')
    html =  response.content.decode('gbk')
#    filename = 'funds_stock.html'
#    html = open(filename, 'rb').read().decode('gbk')
    html_tree = lxml.html.fromstring(html)

    tables = html_tree.xpath('//table')

    # 抽取其中的“截止日期:2014-06-30"的字眼
    temp = tables[5].xpath('.//tr/td[1]/text()')[0]
    public_date = datetime.strptime(temp.split(':')[1], '%Y-%m-%d').date()

    stock_names = tables[6].xpath('.//tr/td[2]/text()')
    stock_codes = tables[6].xpath('.//tr/td[3]/text()')

    for code, name in itertools.izip(stock_codes, stock_names):
        print code, name

#if __name__ == "--main__":
#    test()
