# -*- coding: utf-8 -*-
import scrapy

import re
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from ourku.items import FundStockItem

class BasicInfoSpider(scrapy.Spider):
    name = "basic_info"
    allowed_domains = ["www.ourku.com"]
    #start_urls = (
    #    'http://www.www.ourku.com/',
    #)
    start_urls = []

    engine = create_engine('postgresql://lxq@localhost/funds_data')
    Base = automap_base()
    Base.prepare(engine, reflect = True)

    StockList = Base.classes.stock_list
    FundsList = Base.classes.funds_list
    FundsStockData = Base.classes.funds_stock_data

    Session = sessionmaker()
    session = Session(bind = engine)



    def __init__(self, category=None, *args, **kwargs):
        super(BasicInfoSpider, self).__init__(*args, **kwargs)
        basic_urls = 'http://www.ourku.com/ccmx/'
        
        funds = [x[0] for x in self.session.query(self.FundsList.fund_code).all()]

        for fund in funds:
            self.start_urls.append(basic_urls + fund)
     
    def parse(self, response):
        fund_code = re.findall('\d+', response.url)[0]
        self.log('Start parse %s' % response.url, scrapy.log.INFO)

        temp = response.xpath('//td[@width="50%"]/text()').extract()
        try:
            temp_str = temp[0].split(':')[1]
            public_date = datetime.strptime(temp_str, '%Y-%M-%d').date()
        except:
            self.log('Error occured when extract public_date', scarpy.log.ERROR)
            yield

        try:
            stock_names = response.xpath('//table[@class="in_table"][1]//tr/td[2]/text()').extract()
            stock_codes = response.xpath('//table[@class="in_table"][1]//tr/td[3]/text()').extract()
            stock_amounts = response.xpath('//table[@class="in_table"][1]//tr/td[4]/text()').extract()
            stock_values = response.xpath('//table[@class="in_table"][1]//tr/td[5]/text()').extract()
            stock_value_ratios = response.xpath('//table[@class="in_table"][1]//tr/td[6]/text()').extract()

            for k, v in zip(stock_names, stock_codes, stock_amounts, stock_values, stock_value_ratios):
                if k == 0:
                    yield
                else:
                    item = FundStockItem()
                    item['stock_name'] = v[0]
                    item['stock_code'] = v[1]
                    item['stock_amount'] = int(v[2])
                    item['stock_value'] = float(v[3])
                    item['stock_value_ratio'] = float(v[4])
                    item['fund_code'] = fund_code
                    item['public_date'] = public_date
                    yield item
        except Exception as e:
            self.log('Error occured when extract data: %s' % e, scrapy.log.Error)
            yield
        
