#!/usr/bin/python
#coding=utf-8
# 利用urllib2抓取金融界网站上的基金收益数据

# TODO:
# 1、加上一些头浏览器头信息避免被封
# 2、抓取基金公司名称的数据
# 3、抓取基金十大持仓相关的数据

import urllib, urllib2, re, io, os.path, datetime, json

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

def data2mysql(engine,funds,data_date):
    metadata = MetaData(bind=engine)
    Base = declarative_base(metadata)

# Base.metadata.create_all(engine)
    class Funds_list(Base):
        __table__ = Table('funds_list', metadata, autoload=True)
    class Funds_value(Base):
        __table__ = Table('funds_value', metadata, autoload = True)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    funds_code_in = set([ x['fund_code'] for x in funds ])
    funds_code_curr = set([x[0] for x in session.query(Funds_list.fund_code).all()])
    funds_code_new = funds_code_in - funds_code_curr
#    print funds_code_new

#    items = {}
#    i=0
    for fund_data in funds:
       # 如果funds_list表中没有此基金对应的条目则先更新funds_list表
        if fund_data['fund_code'] in funds_code_new:
            item = Funds_list(fund_code=fund_data['fund_code'], \
                                  fund_name = fund_data['fund_name'])
            session.add(item)
    for fund_data in funds:
        # 如果库中已经有此基金对应此日期的数据，则不再更新
        if not session.query(Funds_value.value_data_id).filter(\
            Funds_value.fund_code == fund_data['fund_code'],\
                Funds_value.value_date == data_date).all():
            item = Funds_value(fund_code=fund_data['fund_code'],\
                                   value_date = data_date, \
                                   value_curr = float(fund_data['value_curr']), \
                                   value_leiji = float(fund_data['value_leiji']))
            session.add(item)            
    session.commit()


# 从金融界网站上抓取基金净值数据信息，输入参数为日期
def get_jrj_data(data_date):
    if data_date == 5:
        data_date = data_date - datetime.timedelta(1)
    elif data_date == 6:
        data_date = data_date - datetime.timedelta(2)
           
    if data_date.weekday() == 0:
        data_date_1 = data_date - datetime.timedelta(3)
    else:
        data_date_1 = data_date - datetime.timedelta(1)
        
    datafile_name = 'cache/' + data_date.strftime('%Y%m%d') + \
    'funds_jrj.dat'

    # 如果cache目录下已经有了下载好的数据文件，则不必再下载一次
    if not os.path.exists(datafile_name):
        url = 'http://fund.jrj.com.cn/action/openfund/Yield.jspa'
        para = {'beginDate':(data_date-datetime.timedelta(1)).strftime('%Y%m%d'),\
                    'endDate':data_date.strftime('%Y%m%d')}
        req = urllib2.Request(url,urllib.urlencode(para))
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
    funds =[ {} for x in range(len(funds_raw)) ]
    for line in funds_raw:
        temp  = json.loads(line)
        funds[i] = {'fund_code':temp[1],'fund_name':temp[2],\
                        'value_curr':temp[4], 'value_leiji':temp[6]}
        i = i + 1
    return funds

if __name__ == "__main__":
    engine = create_engine('mysql://lxq:yumeng@localhost/lxq_fundsdb?charset=utf8')
    curr_date = datetime.datetime.now().date()
    t1 = datetime.datetime.now()
    for i in range(365):        
        print u'开始抓取数据' + curr_date.strftime('%Y%m%d') + '...'
        funds = get_jrj_data(curr_date)
        print u'抓取数据耗时 %ss' % (datetime.datetime.now() - t1).total_seconds()
        print u'开始导入数据库...'
        t1 = datetime.datetime.now()
        data2mysql(engine, funds, curr_date)
        print u'导入数据耗时 %ss' % (datetime.datetime.now() - t1).total_seconds()
        curr_date -= datetime.timedelta(1)



  
        
                                        
                                      
    
    






