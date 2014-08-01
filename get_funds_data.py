#!/usr/bin/python
#coding=utf-8
""" 利用urllib2抓取金融界网站上的基金收益数据
USAGE:

 TODO:
 1、加上一些头浏览器头信息避免被封
 2、抓取基金公司名称的数据
 3、抓取基金十大持仓相关的数据
 4、sqlalchemy 映射相关类重用
 5、缺失的数据再针对每一项基金进行抓取

 20140716: 纯净的DB-API访问，并且批量提交insert语句速度会提高很多，由20多秒
 减少到3-5秒, 但是构造SQL语句的过程中由于涉及大量的裸字符串处理，很容易出错。

 20140717: 纯净的DB-API访问更新1600条左右记录费时约3秒，大部分时间在中间那些
 判断处。ORM优化后更新1600条记录费时约12秒，大部分时间在中间那些判断处。

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
def data2db_simple(conn, funds):
    '''利用DB-API实现数据导入到数据库中。
    conn:       符合DB-API规范的数据库连接变量
    funds:      [{'fund_code':, 'fund_name':, 'value_curr':, 'value_leiji':}]
    '''

    cursor = conn.cursor()

    funds_code_in = set([x['fund_code'] for x in funds])

    sql = 'select fund_code from funds_list'
    cursor.execute(sql)
    funds_code_curr = set([x[0] for x in cursor.fetchall()])

    # 新的基金列表集合
    funds_code_new = funds_code_in - funds_code_curr
    funds_list_values = []
    funds_value_values = []
    for fund_data in funds:
        # 如果原有的基金列表中没有些基金，则先更新基金列表
        if fund_data['fund_code'] in funds_code_new:
            temp = u"('{0}', '{1}')".format(fund_data['fund_code'],
                    fund_data['fund_name'])
            funds_list_values.append(temp)

        # 查询funds_value数据库中有没有对应的数据
        sql = '''select value_data_id from funds_value
        where fund_code = '{0}' and value_date = '{1}' '''.format(
                fund_data['fund_code'],
                '{0}'.format(fund_data['value_date'].strftime('%Y-%m-%d')))
        cursor.execute(sql)

        #如果没有对应的数据则更新
        if not cursor.fetchall():
            temp = "('{0}', {1}, {2}, '{3}')".format(
                    fund_data['fund_code'],
                    fund_data['value_curr'],
                    fund_data['value_leiji'],
                    '{0}'.format(fund_data['value_date'].strftime('%Y-%m-%d')))
            funds_value_values.append(temp)

    # 利用上述数据构造SQL语句并执行向funds_list表中插入数据
    if funds_list_values:
        sql = 'insert into funds_list (fund_code, fund_name) values '
        sql += ','.join(funds_list_values)
        cursor.execute(sql)
        conn.commit()

    # 利用上述数据构造SQL语句并执行向funds_value表中插入数据
    if funds_value_values:
        sql = '''insert into funds_value
        (fund_code, value_curr, value_leiji, value_date) values '''
        sql += ','.join(funds_value_values)
        cursor.execute(sql)
        conn.commit()
        return len(funds_value_values)
    else:
        return 0


def data2db(engine,funds):
    '''利用sqlalchemy实现数据导入到数据库中。
    engine:     输入的sqlalchemy engine变量
    funds:      [{'fund_code':, 'fund_name':, 'value_curr':, 'value_leiji':}]
    返回值：    更新的净值记录数
    '''
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

    funds_list_items=[]
    funds_value_items=[]
    for fund_data in funds:
       # 如果funds_list表中没有此基金对应的条目则先更新funds_list表
        if fund_data['fund_code'] in funds_code_new:
            funds_list_items.append(fund_data)

        # 如果库中已经有此基金对应此日期的数据，则不再更新
        if not session.query(Funds_value.value_data_id).filter(
                Funds_value.fund_code == fund_data['fund_code'],
                Funds_value.value_date == fund_data['value_date']).all():
            funds_value_items.append(fund_data)
    if funds_list_items:
        session.execute(Funds_list.__table__.insert(), 
                funds_list_items)
        session.commit()
    if funds_value_items:
        session.execute(Funds_value.__table__.insert(),
                funds_value_items)
        session.commit()
        return len(funds_value_items)
    else:
        return 0

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
    # 当天的数据解析和历史数据不一样，现不支持当天的数据
    if data_date >= today:
        print(u'不支持当天和未来的数据抓取，仅支持历史数据抓取')
        return []

    temp_filename =  '/tmp/ourku.com-' + str(data_date) + '.dat'
    if os.path.exists(temp_filename):
        the_page = file(temp_filename,'r').read()
    else:
        url = r'http://www.ourku.com/indexMore.php'
        para = {'date':data_date.strftime('%Y-%m-%d')}
        req = urllib2.Request(url,urllib.urlencode(para))
        response = urllib2.urlopen(req)
        the_page = response.read()
        file(temp_filename,'w').write(the_page)
    the_page = the_page.decode('gbk')

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
    funds_data = [{'fund_code':x[0],
        'fund_name':x[1],
        'value_curr':x[2],
        'value_leiji':x[3],
        'value_date':data_date}
        for x in funds_data]
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
        db_user = cf.get('database', 'db_user')
        db_pass = cf.get('database', 'db_pass')
        db_host = cf.get('database', 'db_host')
        db_name = cf.get('database', 'db_name')
        dbms = cf.get('database', 'dbms')
        curr_date_str = cf.get('fetch', 'curr_date')
        if curr_date_str == '':
            curr_date = datetime.datetime.now().date()
        else:
            curr_date = datetime.datetime.strptime(curr_date_str, '%Y%m%d').date()

        try:
            date_range = cf.getint('fetch','date_range')
        except:
            date_range = 1
    else:
        db_user = args.user
        db_pass = args.passwd
        db_host = args.host
        db_name = args.db
        curr_date = datetime.datetime.now().date()
        date_range = 1
    if dbms == 'mysql':
        engine_str = 'mysql://%s:%s@%s/%s?charset=utf8' % (db_user,db_pass,db_host,db_name)
    elif dbms == 'postgresql':
        engine_str = 'postgres://%s:%s@%s/%s' % (db_user,db_pass,db_host,db_name)
    else:
        raise Exception('Error dbms parameter in configure file!')

    try:
        engine = create_engine(engine_str)
        # connect = engine.connect()
        import psycopg2
        connect = psycopg2.connect(database = db_name, user = db_user,
                password=db_pass, host = db_host)
    except:
        print "请输入正确的数据库相关参数，或者通过命令行或者通过配置文件"

    t1 = datetime.datetime.now()
    for i in range(date_range):
        print u'开始抓取数据' + curr_date.strftime('%Y%m%d') + '...'
        funds = get_ourku_data(curr_date)
        print u'抓取数据耗时 %ss' % (datetime.datetime.now() - t1).total_seconds()

        t1 = datetime.datetime.now()

        if funds:
            print u'开始导入数据库... %s' % funds[0]['value_date'].strftime('%Y%m%d')
            rec_num = data2db_simple(connect, funds)


            print u'共导入数据: {0}条，导入数据耗时: {1}s'.format(rec_num, 
                (datetime.datetime.now() - t1).total_seconds())
        else:
            print('抓取到的数据为0，自动跳过，检查是否此日期为节假日')
        curr_date -= datetime.timedelta(1)
