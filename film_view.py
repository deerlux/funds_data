#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import matplotlib.pyplot as plt
import pandas as pd
from pandas.io.excel import read_excel

import numpy as np

import matplotlib

def baidu_index(filename, pub_date = None):
    try:
        temp = read_excel(filename)
    except IOError as msg:
        print e
        return None
    
    ds = [x.date() for x in temp['收集时间']]
    baidu_f = pd.DataFrame(temp['搜索指数'].tolist(), index=ds, 
            columns=temp['搜索关键字'].unique())
    baidu_f2 = baidu_f.groupby(level=0).max()
        
    if pub_date :
        delta_days = [x.days for x in 
            baidu_f2.index.values - np.repeat(pub_date, len(baidu_f2.index))]
        baidu_f2.index = delta_days

    return baidu_f2


def douban_comment(filename, pub_date=None):
    try:
        temp = read_excel(filename)
    except IOError as e:
        print e
        return None
    
    ds = [x.date() for x in temp['收集时间']]

    douban_f = pd.DataFrame(temp['评价人数增量'].tolist(), index = ds, 
        columns = temp['电影名称'].unique())
    
    douban_f2 = douban_f.groupby(level=0).max()

    if pub_date:
        delta_days = [x.days for x in 
            douban_f2.index.values - np.repeat(pub_date, len(douban_f2.index))]
        douban_f2.index = delta_days

    return douban_f2


if __name__ == '__main__':
    """如果要显示中文，则修改mpl_data/XXXrc文件，将family以及sans-serif相关的内
    容改一下"""

#    matplotlib.rcParams['font.sans-serif']=['WenQuanYi Micro Hei']
#    myfont = matplotlib.font_manager.FontProperties(fname='/usr/share/fonts/wenquanyi/wqy-microhei/wqy-microhei.ttc')

    baidu_f2 = baidu_index('baidu_index.xls', pd.datetime(2014,12,5).date())

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    ax.plot(baidu_f2.index, baidu_f2['匆匆那年'].values,label ='百度搜索指数',
            linewidth = 2.5)
    ax.set_xlabel('与上映首日间隔')
    ax.set_xlim(0, 20)
    ax.set_yscale('log')

    douban_f2 = douban_comment('douban_film_score.xls', 
            pd.datetime(2014,12,5).date())

    ax.plot(douban_f2.index, douban_f2['匆匆那年'].values, 
            label = '豆瓣评价增量')
    ax.legend(loc='best')
    ax.grid('on')
    
    plt.show()

