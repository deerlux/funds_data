#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

import matplotlib.pyplot as plt
import pandas as pd
from pandas.io.excel import read_excel
import numpy as np

import matplotlib
from matplotlib.font_manager import fontManager

import os.path
import os
import datetime


class PiaoFangAnalyze:

    def __init__(self, dirname, pub_date=None):
        self.pub_date = pub_date
        self.film_name = os.path.basename(dirname)

        self.baidu_fname = dirname + os.path.sep + 'baidu_index.xls'
        self.douban_fname = dirname + os.path.sep + 'douban_film_score.xls'
        self.gewara_fname = dirname + os.path.sep + 'gewara.xls'
        self.piaofang_history_fname = dirname + os.path.sep + \
                'piaofang168_history.xls'
        self.piaofang_realtime_fname = dirname + os.path.sep + \
                'piaofang168_realtime.xls'


def __diff_date(pub_date, ds):
    if pub_date:
        result = [x.days for x in ds - np.repeat(pub_date, len(ds))]
    else:
        result = ds
    
    return result


def baidu_index(filename, pub_date = None):
    try:
        temp = read_excel(filename)
    except IOError as msg:
        print(e)
        return None
    
    ds = [x.date() for x in temp['收集时间']]
    temp.index = __diff_date(pub_date, ds)

    baidu_f = temp.drop(['内部编号','搜索类型','搜索排名',
        '搜索趋势','收集时间','更新时间'], axis=1).groupby(level=0).max()
        
    return baidu_f


def douban_comment(filename, pub_date=None):
    try:
        temp = read_excel(filename)
    except IOError as e:
        print(e)
        return None
    
    ds = np.array([x.date() for x in temp['收集时间']])
    temp.index = __diff_date(pub_date, ds)

    douban_f = temp.drop(['内部编号','豆瓣编号',
        '收集时间','更新时间'], axis = 1)

    return douban_f


def gewara_data(filename, pub_date):
    try:
        temp = read_excel(filename)
    except IOError as e:
        print(e)
        return None

    ds = [x.date() for x in temp['收集时间']]
    temp.index = __diff_date(pub_date, ds)

    gewara_f = temp.drop(['内部编号', '格瓦拉编号', 
        '收集时间', '更新时间'], axis=1).groupby(level=0).max()

    return gewara_f


def piaofang_data(filename, pub_date):
    try:
        temp = read_excel(filename)
    except IOError as e:
        print(e)
        return None

    ds = [x.date() for x in temp['发布时间']]
    temp.index = __diff_date(pub_date, ds) 
    
    piaofang_f = temp.drop(['内部编号','发布时间','收集时间','更新时间'],
            axis=1).groupby(level=0).max()
    
    return piaofang_f


if __name__ == '__main__':
    """如果要显示中文，则修改mpl_data/XXXrc文件，将family以及sans-serif相关的内
    容改一下"""

    fontManager.defaultFont['ttf']='~/.fonts/msyh.ttf'
    matplotlib.rcParams['font.sans-serif']=['Microsoft YaHei']
    matplotlib.rcParams['font.family']=['sans-serif']

    pub_date = pd.datetime(2014,12,5).date()

    baidu_f = baidu_index('baidu_index.xls', pub_date)

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    ax.plot(baidu_f.index, baidu_f['搜索指数'].values, label ='百度搜索指数',
            linewidth = 2.5)
    ax.set_xlabel('与上映首日间隔')


    douban_f = douban_comment('douban_film_score.xls', pub_date)

#    ax.plot(douban_f2.index, douban_f2['匆匆那年'].values, 
#            label = '豆瓣评价增量', linewidth = 2.5)

    gewara_f = gewara_data('gewara.xls', pub_date)
    ax.plot(gewara_f.index, 
            gewara_f['喜欢人数增量'].values, label='gewara喜欢人数增量',
            linewidth = 2.5)
    ax.plot(gewara_f.index, 
            gewara_f['关注人数增量'].values, label='gewara关注人数增量',
            linewidth = 2.5)
    ax.plot(gewara_f.index,
            gewara_f['购买人数增量'].values, label='gewara购买人数增量',
            linewidth = 2.5)
#    gewara_f.plot(ax=ax, linewidth = 2.5)
    ax.set_xlim(0,20)

    ax.legend(loc='best')
    ax.grid('on')
    ax.set_title('匆匆那年')
    ax.set_yscale('log')
    
    plt.xticks(rotation=45)
    

    pf_f = piaofang_data('piaofang168_history.xls', pub_date)
    
    #fig2=plt.figure()
    #ax2 = fig2.add_subplot(1,1,1)
    plt.plot(pf_f.index, pf_f['今日票房/万'], label = '票房情况', linewidth=2.5)

    dates = [pub_date+x for x in [datetime.timedelta(y) for y in range(0,21)]]
    for k,v in enumerate(dates):
        if v.weekday() == 5:
            ax.fill_between([k, k+1], ax.get_ylim()[0], 
                    ax.get_ylim()[1], alpha=0.3)

    fig.savefig('匆匆那年_log.png')
      
    plt.show()

