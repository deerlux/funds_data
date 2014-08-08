#!/usr/bin/env python
# -*- coding=utf8 -*-

import ConfigParser
import sys

from OurkuFundsInfoFetcher import OurkuFundsInfoFetcher
from FundsDataDB import FundsDataDB


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

    funds_code = db.session.query(db.FundsList.fund_code).all()
    print('\n'.join([x[0] for x in funds_code[0:20] ]))

