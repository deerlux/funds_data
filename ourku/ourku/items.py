# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FundStockItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    stock_code = scrapy.Field()
    stock_name = scrapy.Field()
    stock_amount = scrapy.Field()
    stock_value = scrapy.Field()
    stock_value_ratio = scrapy.Field()
    fund_code = scrapy.Field()
    public_date = scrapy.Field()
    
