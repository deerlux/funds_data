#!/usr/bin/env python
# -*- coding=utf8 -*-

import ConfigParser
import sys

from OurkuFundsInfoFetcher import OurkuFundsInfoFetcher
from FundsDataDB import FundsDataDB
from sqlalchemy.exc import IntegrityError

def update_stock(fethcer, db, tmp_path='/tmp'):
    '''Update the funds_stock_data and stock_data table.
    fetcher     OurkuFundsInfoFetcher object.
    db          initialized FundsDataDB object.
    tmp_path    the path of temp html files saved.'''

    result = db.query(db.FundsList.fund_code).\
            values(db.FundsList.fund_code)

    for i, v in enumerate(result):
        print('Starting update the stock data of %s' % v.fund_code)

        try:
            fetcher.init(v.fund_code, tmp_path = tmp_path)
            stock_data = fetcher.iget_stock_data()
        except IndexError:
            print('Failed to fetch the stock data of %s' % v.fund_code)
            #raise        

        for item in stock_data:
            if  not db.query(db.StockList).filter_by(\
                    stock_code = item['stock_code']).first():
                row = db.StockList(stock_code = item['stock_code'],
                        stock_name = item['stock_name'])
                db.add(row)
                db.commit()
                #print('stock list updated:  %s: %s' % (item['stock_code'], 
                #    item['stock_name']))
            row = db.FundsStockData(fund_code = item['fund_code'],
                    stock_code = item['stock_code'],
                    public_date = item['public_date'],
                    stock_amount = item['stock_amount'],
                    stock_value = item['stock_value'],
                    stock_value_ratio = item['stock_value_ratio'])
            try:
                db.add(row)
                db.commit()
                #print('funds_stock data updated: %s->%s' % (item['fund_code'],
                #    item['stock_code']))
            except IntegrityError as e:
                print(e)
                db.rollback()
        if i % 50 == 0:
            print('Funds stock data updated: %d' % i)


def update_basic(fetcher, db, tmp_path='/tmp'):
    '''Update the basic information of funds.
    fetcher     OurkuFundsInfoFetcher object
    db          initialized FundsDataDB object
    tmp_path    the path of the temp html file saved. 
    return      count of records that was updated.'''

    # get the iterator 
    result = db.query(db.FundsList.fund_code).\
            values(db.FundsList.fund_code)

    count = 0
    for i, v in enumerate(result):
        print('Starting fetch the information of fund "%s"...' % v.fund_code)
        try:
            # fetch the basic fund information
            fetcher.init(v.fund_code, tmp_path=tmp_path)
            basic_info = fetcher.get_fund_basic()
            type_query = db.query(db.FundsType.type_id).filter_by(
                    type_name = basic_info['fund_type']).first()

            # insert funds_type when the type is no exists.
            if type_query == None:
                try:
                    item = db.FundsType(type_name = basic_info['fund_type'])
                    db.add(item)
                    db.commit()
                    type_id = db.query(db.FundsType.type_id).\
                        filter_by(type_name = basic_info['fund_type']).\
                        first().type_id
                    print(u'Added a new type : %s' % basic_info['fund_type'])
                except IntegrityError as e:
                    print('Inserting error %s' % v.fund_code)
                    print(e)
                    db.rollback()
                    db.session.close()
                    type_id = None
                    raise
            else:
                type_id = type_query.type_id
            print('Type id is: %d', type_id)

            row = db.query(db.FundsList).\
                    filter_by(fund_code=v.fund_code)
            
            row.update({db.FundsList.type_id:type_id,
                db.FundsList.fund_origin_date:basic_info['origin_date']})
            count += 1
        except IndexError as ie:
            print('fetch data failed: %s' % v.fund_code)
            print ie
    db.commit()

    return count


if __name__ == "__main__":
    usage = '''Usage:
    test <config file>'''
    cf = ConfigParser.ConfigParser()
    if len(sys.argv) >1:
        cf.read(sys.argv[1])
        db_user = cf.get('database', 'db_user')
        db_pass = cf.get('database', 'db_pass')
        db_host = cf.get('database', 'db_host')
        db_name = cf.get('database', 'db_name')
        dbms = cf.get('database', 'dbms')
    else:
        print(usage)
        sys.exit(0)
    
    db = FundsDataDB(user = db_user, password = db_pass, db_name = db_name,
            host = db_host, dbms = dbms)
    
    fetcher = OurkuFundsInfoFetcher()
    
    # count = update_basic(fetcher, db, './temp')
    update_stock(fetcher, db, './temp')


#    print('\n'.join([x[0] for x in funds_code[0:20] ]))

