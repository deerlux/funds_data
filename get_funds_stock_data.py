#!/usr/bin/python
# -*- coding: utf8 -*-
import lxml.html
from datetime import datetime
import itertools
import requests
import os.path

def get_ourku_funds_stock_data(fund_code, season=0):
    '''从ourku.com网站上抓取基金的持仓股票数据.
    fund_code   要抓取的基金代码
    season      抓取哪个季度的数据，默认情况下为0，表示抓取本季度数据，如果为1
                则表示抓取上推一个季度的数据，依次类推
    返回值      为字典列表:[{'fund_code': fund_code, 'stock_code': stock_code,
                            'public_date':public_date}]'''

    tmpfilename = '/tmp/ourku.com-{0}_{1}.html'.format(fund_code, season)

    if os.path.exists(tmpfilename):
        html = open(tmpfilename,'rb').read().decode('gbk')
    else:
        url = 'http://www.ourku.com/ccmx/{0}/'.format(fund_code)
        response = requests.get(url)
        html =  response.content

        open(tmpfilename,'wb').write(html)

        html = html.decode('gbk')

    html_tree = lxml.html.fromstring(html)
    
    tables = html_tree.xpath('//table')

    # 抽取其中的“截止日期:2014-06-30"的字眼
    temp = tables[5].xpath('.//tr/td[1]/text()')[0]
    public_date = datetime.strptime(temp.split(':')[1], '%Y-%m-%d').date()

    stock_names = tables[6].xpath('.//tr/td[2]/text()')
    stock_codes = tables[6].xpath('.//tr/td[3]/text()')

    # delete the table header data
    if stock_codes:
       stock_codes.pop(0)
    else:
        return []
    if stock_names:
        stock_names.pop(0)
    else:
        return []
    
    result = []
    for code, name in itertools.izip(stock_codes, stock_names):
        temp = {'fund_code':fund_code, 'stock_code':code, 
                'stock_name':name,'public_date':public_date}
        result.append(temp)

    return result

if __name__ == "__main__":
    stock_data = get_ourku_funds_stock_data('519996')
    print stock_data
