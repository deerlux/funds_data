#!/usr/bin/python
from sqlalchemy import *
from sqlalchemy.orm import create_session
from sqlalchemy.ext.declarative import declarative_base

if __name__ == "__main__":
#def data2mysql(funds):
    engine = create_engine('mysql://lxq:yumeng@localhost/lxq_fundsdb?charset=utf8',echo=True)

    metadata = MetaData(bind=engine)
    Base = declarative_base(metadata)

# Base.metadata.create_all(engine)
    class Funds_list(Base):
        __table__ = Table('funds_list', metadata, autoload=True)
    
    session = create_session(bind = engine)

    testlist = session.query(Funds_list).all()
    print testlist
    help(testlist)


# print testlist[0].fund_code, testlist[0].fund_name.decode('utf-8')
# help(Funds_list)
