#!/usr/bin/python
#coding=utf-8
# 利用urllib2抓取金融界网站上的基金收益数据

# TODO:
# 1、改变输入参数定期从网上抓取所有的数据，加上一些头浏览器头信息避免被封
# 2、使输入的设置更为灵活，日期的输入避免输入周末，datetime.date.weekday() ~= 5,6
# 3、判断库中已有的数据
# 4、抓取基金公司名称的数据
# 5、抓取基金十大持仓相关的数据

import urllib, urllib2, re, io, os.path, datetime, json

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

def data2mysql(funds,data_date):
    engine = create_engine('mysql://lxq:yumeng@localhost/lxq_fundsdb?charset=utf8')

    metadata = MetaData(bind=engine)
    Base = declarative_base(metadata)

# Base.metadata.create_all(engine)
    class Funds_list(Base):
        __table__ = Table('funds_list', metadata, autoload=True)
    class Funds_value(Base):
        __table__ = Table('funds_value', metadata, autoload = True)
    
    Session = sessionmaker(bind=engine)
    session = Session()

    fund_data = {}
    
    for temp in funds:
        fund_data['fund_code'] = temp[1]
        fund_data['fund_name'] = temp[2]
        fund_data['value_curr'] = temp[4]
        fund_data['value_leiji'] = temp[6]
        # 如果funds_list表中没有此基金对应的条目则先更新funds_list表
        if session.query(Funds_list).filter(Funds_list.fund_code == fund_data['fund_code']):
            item = Funds_list(fund_code=fund_data['fund_code'], \
                                  fund_name = fund_data['fund_name'])
            session.add(item)
        item = Funds_value(fund_code=fund_data['fund_code'],\
                               value_date = data_date, \
                               value_curr = float(fund_data['value_curr']), \
                               value_leiji = float(fund_data['value_leiji']))
        session.add(item)
    session.commit()

if __name__ == "__main__":

    datafile_name = 'cache/' + datetime.datetime.now().date().strftime('%Y%m%d') + \
    'funds_jrj.dat'

    # 如果cache目录下已经有了下载好的数据文件，则不必再下载一次
    if not os.path.exists(datafile_name):
        url = 'http://fund.jrj.com.cn/action/openfund/Yield.jspa'
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        the_page = response.read().decode('gbk')
        datafile = io.open(datafile_name, 'w')
        datafile.write(the_page)
        datafile.close()
    else:
        datafile = io.open(datafile_name,'r')
        the_page = datafile.read()
        datafile.close()
    # 匹配出基金相关的数据
    pattern = re.compile(r'(?<=JSON_DATA.push\()(.+)(?=\);)')
    funds_raw = pattern.findall(the_page)

    # 将匹配出的数据转换为字符串二维数组
    i = 0
    funds =[ ['' for col in range(10)] for x in range(len(funds_raw)) ]
    for temp in funds_raw:
        funds[i] = json.loads(temp)    
        #    for j in range(10):
        #        print funds[i][j]
        i = i + 1

    data2mysql(funds, datetime.datetime.now().date())


  
        
                                        
                                      
    
    






