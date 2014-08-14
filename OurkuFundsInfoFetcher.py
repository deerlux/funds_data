#!/usr/bin/python
# -*- coding: utf8 -*-
from __future__ import with_statement
import lxml.html
from datetime import datetime
import itertools
import requests
import os.path

class OurkuFundsInfoFetcher:
    '''从ww.wourku.com/ccmx/nnnnnn/主页抓取基金持仓、基金规模、基金类型等信息。
    '''


    def __init__(self, fund_code='', season = 0, tmp_path = '/tmp'):
        '''以基金代码为初始化参数，抓取相关的数据，并将其存储在self.html变量
        中。'''
        if fund_code:
            self.init(fund_code, season, tmp_path)
        else:
            pass

    def init(self, fund_code, season = 0, tmp_path='/tmp'):
        ''' The __init__ method replacement, used to call directly.'''
        self.fund_code = fund_code

        tmpfilename = os.path.join(tmp_path,
            'ourku.com-ccmx-{0}_{1}.html'.format(fund_code, season))

        if os.path.exists(tmpfilename):
            self.html = open(tmpfilename,'rb').read().decode('gbk')
        else:
            url = 'http://www.ourku.com/ccmx/{0}/'.format(fund_code)
            response = requests.get(url)
            self.html =  response.content

            with open(tmpfilename,'wb') as f:
                f.write(self.html)

            self.html = self.html.decode('gbk')

    def iget_stock_data(self):
        '''从ourku.com网站上抓取基金的持仓股票数据.
    fund_code   要抓取的基金代码
    season      抓取哪个季度的数据，默认情况下为0，表示抓取本季度数据，如果为1,
                则表示抓取上推一个季度的数据，依次类推
    返回值      为字典迭代器:[{'fund_code': fund_code, 'stock_code': stock_code,'public_date':public_date}]'''

        html_tree = lxml.html.fromstring(self.html)
    
        tables = html_tree.xpath('//table')
        if not tables:
            raise StopIteration

        try:
            # 抽取其中的“截止日期:2014-06-30"的字眼
            temp = tables[5].xpath('.//tr/td[1]/text()')[0]
            public_date = datetime.strptime(temp.split(':')[1], 
                    '%Y-%m-%d').date()
        except:
            public_date = None

        try:
            stock_names = tables[6].xpath('.//tr/td[2]/text()')
            stock_codes = tables[6].xpath('.//tr/td[3]/text()')
            stock_amount = tables[6].xpath('.//tr/td[4]/text()')
            stock_value = tables[6].xpath('.//tr/td[5]/text()')
            stock_value_ratio = tables[6].xpath('.//tr/td[6]/text()')
        except:
            raise StopIteration

        # delete the table header data
        if stock_codes:
           stock_codes.pop(0)
           stock_names.pop(0)
           stock_amount.pop(0)
           stock_value.pop(0)
           stock_value_ratio.pop(0)
        else:
            raise StopIteration
   
        for code, name, amount, value, value_ratio in itertools.izip(
                stock_codes, stock_names, stock_amount, stock_value,
                stock_value_ratio):
            yield {'fund_code':self.fund_code, 'stock_code':code, 
                    'stock_name':name, 'public_date':public_date,
                    'stock_amount':int(amount), 'stock_value':float(value), 
                    'stock_value_ratio':float(value_ratio)}


    def get_fund_basic(self):
        ''' Fetch the basic infomation of funds from ourku.com/ccmx/nnnnnn
pages.

    return value:   {'fund_type':fund_type, 'amount':amount,'origin_date':origin_date}'''  
        html_tree = lxml.html.fromstring(self.html)
        tables = html_tree.xpath('//table')
        table = tables[2]
        tds = table.xpath('./tr/td/text()')

        fund_type = tds[0].split(u'\xa0')[0].split(u'：')[1]
        origin_date = tds[1].split(u'\xa0')[0].split(u'：')[1]
        amount = tds[1].split(u'\xa0')[2].split(u'：')[1]

        # 抽取其中的“截止日期:2014-06-30"的字眼
        temp = tables[5].xpath('.//tr/td[1]/text()')[0]
        public_date = datetime.strptime(temp.split(':')[1], '%Y-%m-%d').date()

        temp = amount.split(' ')
        if temp[1] == u'亿份':
            amount = float(temp[0]) * 1e8
        else:
            print("The unit of fund amount if invalid: %s" % self.fund_code)
            amount = float(temp[0])

        try:
            origin_date = datetime.strptime(origin_date, '%Y-%m-%d').date()
        except:
            origin_date = None


        return {'fund_type':fund_type, 'amount':amount, 
                'origin_date':origin_date, 'public_date':public_date}


if __name__ == "__main__":
    fetcher = OurkuFundsInfoFetcher('519996')

    stock_data = fetcher.iget_stock_data() 
    print list(stock_data)

    fund_info = fetcher.get_fund_basic()
    for key in fund_info:
        print key, fund_info[key]
