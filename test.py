#!/usr/bin/env python
# -*- coding=utf8 -*-

import ConfigParser
import sys

from OurkuFundsInfoFetcher import OurkuFundsInfoFetcher
from FundsDataDB import FundsDataDB
from sqlalchemy.exc import IntegrityError


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
    
    # get the iterator 
    result = db.query(db.FundsList.fund_code).\
            values(db.FundsList.fund_code)

    fetcher = OurkuFundsInfoFetcher()

    count = 0
    for i, v in enumerate(result):
        print('Starting fetch the information of fund "%s"...' % v.fund_code)
        try:
            # fetch the basic fund information
            fetcher.init(v.fund_code)
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

    print('%d records is updated' % count)
#        if i == 10:
#            break

    db.commit()
#    print('\n'.join([x[0] for x in funds_code[0:20] ]))

