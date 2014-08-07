#!/usr/bin/env python
# -*- coding=utf8 -*-

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

class FundsDataDB:
    '''The class implement the "funds_data" database API'''

    def __init__(self, user, password, db_name,
            host = 'localhost', 
            dbms = 'postgresql'):
        '''init the database'''
        if dbms == 'postgresql':
            engine_str = 'postgres://%s:%s@%s/%s' % (user,
                    password, host, db_name)
        elif dbms == 'mysql':
            engine_str = 'mysql://%s:%s@%s/%s?charset=utf8' % (user,
                    password, host, db_name)
        else:
            print("The dbms %s is not supported!" % dbms)
            raise Exception

        self.engine = sqlalchemy.create_engine(engine_str)
        
        Session = sessionmaker(bind = self.engine)
        self.session = Session()

        metadata = sqlalchemy.MetaData(bind = self.engine)
        Base = declarative_base(metadata)

        class FundsList(Base):
            __table__= sqlalchemy.Table('funds_list', metadata,
                    autoload = True)
        class FundsValue(Base):
            __table__ = sqlalchemy.Table('funds_value', metadata, 
                    autoload = True)
        class FundsStockData(Base):
            __table__ = sqlalchemy.Table('funds_stock_data', metadata, 
                    autoload = True)
        class FundsAmount(Base):
            __table__ = sqlalchemy.Table('funds_amount', metadata,
                    autoload = True)
        class FundsType(Base):
            __table__ = sqlalchemy.Table('funds_type', metadata,
                    autoload = True)
        self.FundsList = FundsList
        self.FundsValue = FundsValue
        self.FundsStockData = FundsStockData
        self.FundsAmount = FundsAmount
        self.FundsType = FundsType


    def __del__(self):
        self.session.close()

