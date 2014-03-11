#!/usr/bin/python
#coding=utf-8
# 利用urllib2抓取金融界网站上的基金收益数据
import urllib
import urllib2
import re
import io
import os.path
import datetime

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
pattern = re.compile(r'(?<=JSON_DATA.push\(\[)(.+)(?=\]\);)')
funds_raw = pattern.findall(the_page)

# 将匹配出的数据转换为字符串二维数组
i = 0
funds =[ ['' for col in range(10)] for x in range(len(funds_raw)) ]
for temp in funds_raw:
    funds[i] = temp.split(',')
    for j in range(1,9):
        funds[i][j] = funds[i][j].split('"')[1]
    i = i + 1
#for x in funds[1]:
#    print x




