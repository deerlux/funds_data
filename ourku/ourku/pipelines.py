# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from ourku.items import FundStockItem
from ourku.spiders.basic_info import BasicInfoSpider

from scrapy import log

class OurkuPipeline(object):
    def process_item(self, item, spider):
        if type(item) != FundStockItem:
            return item
        
        StockList = BasicInfoSpider.StockList
        FundsList = BasicInfoSpider.FundsList
        FundsStockData = BasicInfoSpider.FundsStockData
        session = BasicInfoSpider.session

        stock_avail = session.query(StockList).filter(
                StockList.stock_code == item['stock_code']).all()

        if len(stock_avail) == 0:
            db_item = StockList()
            db_item.stock_code = item['stock_code']
            db_item.stock_name = item['stock_name']
            session.add(db_item)
            try:
                session.commit()
            except Exception as e:
                log.msg(str(e), level = log.INFO)
                session.rollback()


        db_item = FundsStockData()
        db_item.fund_code = item['fund_code']
        db_item.public_date = item['public_date']
        db_item.stock_code = item['stock_code']
        db_item.stock_name = item['stock_name']
        db_item.stock_value = item['stock_value']
        db_item.stock_value_ration = item['stock_value_ratio']

        session.add(db_item)
        try:
            session.commit()
            log.msg('%s -> %s is inserted' % (item['fund_code'], item['stock_code']))
        except Exception as e:
            log.msg(str(e), level = log.WARNING)
            session.rollback()
        

        return item
