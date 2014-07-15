#!/usr/bin/python
#coding=utf-8
""" 利用urllib2抓取金融界网站上的基金收益数据
USAGE:

 TODO:
 1、加上一些头浏览器头信息避免被封
 2、抓取基金公司名称的数据
 3、抓取基金十大持仓相关的数据
 4、sqlalchemy 映射相关类重用

@author $author$
$Id$

"""

import urllib, urllib2, re, io, os.path, datetime, json
import ConfigParser

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import argparse

def weekend_proc(in_date):
    '''判断是否是周末，如果是周末的话自动将日期减1或2换算成周五
    in_date     是一个日期类型的变量
    返回值：    更新后的日期'''
    weekday = in_date.weekday()
    if weekday == 5:
        return in_date - datetime.timedelta(1)
    elif weekday == 6:
        return in_date - datetime.timedelta(2)
    else:
        return in_date

def data2db(engine,funds):
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
                Funds_value.value_date == fund_data['value_date']).all():
            item = Funds_value(fund_code=fund_data['fund_code'],\
                                   value_date = fund_data['value_date'], \
                                   value_curr = float(fund_data['value_curr']), \
                                   value_leiji = float(fund_data['value_leiji']))
            session.add(item)            
    session.commit()


# 从金融界网站上抓取基金净值数据信息，输入参数为日期
def get_jrj_data(data_date):
    weekday = data_date.weekday()
    if weekday == 5:
        data_date = data_date - datetime.timedelta(1)
    elif weekday == 6:
        data_date = data_date - datetime.timedelta(2)
           
    if weekday == 0:
        data_date_1 = data_date - datetime.timedelta(3)
    else:
        data_date_1 = data_date - datetime.timedelta(1)
        
    datafile_name = '/tmp/' + data_date.strftime('%Y%m%d') + \
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
                        'value_curr':temp[4], 'value_leiji':temp[6], \
                        'value_date':data_date}
        i = i + 1
    return funds

def get_ourku_data(data_date):
    """从ourku.com网站抓取基金数据
    data_date   要抓取的基金数据日期
    返回值：    基金数据字典数据{fund_code:, fund_name: , value_curr:, value_leiji:, value_date: }
    """
    # 获取ourku的数据
    data_date = weekend_proc(data_date)

    today = datetime.date.today()
    if data_date == today:
        url = r'http://www.ourku.com/index.html'
        req = urllib2.Reques(url)
    elif data_date > today:
        print("Error input data_date: %s for `get_ourku_data` function!" % str(data_date))
        return []
    else:
        url = r'http://www.ourku.com/indexMore.php'
        para = {'date':data_date.strftime('%Y-%m-%d')}
        req = urllib2.Request(url,urllib.urlencode(para))
    response = urllib2.urlopen(req)
    the_page = response.read().decode('gbk')
    
    # 用正则表达式过滤基金数据
    date_str = data_date.strftime('%Y-%m-%d')
    temp = '''<td>%s</td>
<td>(\d{6})</td>
<td>(.+)</td>
<td>(.+)</td>
<td>(.+)</td>'''
    pattern = re.compile(temp % data_date.strftime('%Y-%m-%d'))
    funds_data = pattern.findall(the_page)
    
    # 将数据转换成为字典列表的形式
    funds_data = [{'fund_code':x[0], \
            'fund_name':x[1], \
            'value_curr':x[2], \
            'value_leiji':x[3],\
            'value_date':data_date} \
            for x in funds_data_o]
    return funds_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host')
    parser.add_argument('--user')
    parser.add_argument('--passwd')
    parser.add_argument('--db')
    parser.add_argument('configfile',nargs='*')

    args = parser.parse_args()

    cf = ConfigParser.ConfigParser()
    if args.configfile:
        cf.read(args.configfile)
        db_user = cf.get('main', 'db_user')
        db_pass = cf.get('main', 'db_pass')
        db_host = cf.get('main', 'db_host')
        db_name = cf.get('main', 'db_name')
        curr_date_str = cf.get('main', 'curr_date')
        if curr_date_str == '':
            curr_date = datetime.datetime.now().date()
        else:
            curr_date = datetime.datetime.strptime(curr_date_str, '%Y%m%d').date()
        try:
            date_range = cf.getint('main','date_range')
        except:
            date_range = 1
    else:
        db_user = args.user
        db_pass = args.passwd
        db_host = args.host
        db_name = args.db
        curr_date = datetime.datetime.now().date()
        date_range = 1
    engine_str = 'mysql://%s:%s@%s/%s?charset=utf8' % (db_user,db_pass,db_host,db_name)

    try:
        engine = create_engine(engine_str)
        connect = engine.connect()
    except:
        print "请输入正确的数据库相关参数，或者通过命令行或者通过配置文件"

    t1 = datetime.datetime.now()    
    for i in range(date_range):
        print u'开始抓取数据' + curr_date.strftime('%Y%m%d') + '...'
        funds = get_jrj_data(curr_date)
        print u'抓取数据耗时 %ss' % (datetime.datetime.now() - t1).total_seconds()
        print u'开始导入数据库... %s' % funds[0]['value_date'].strftime('%Y%m%d')
        t1 = datetime.datetime.now()
        data2mysql(engine, funds)
        print u'导入数据耗时 %ss' % (datetime.datetime.now() - t1).total_seconds()
        curr_date -= datetime.timedelta(1)

