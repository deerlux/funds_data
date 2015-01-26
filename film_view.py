#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

import matplotlib.pyplot as plt
import pandas as pd
from pandas.io.excel import read_excel
import numpy as np

import matplotlib
from matplotlib.font_manager import fontManager

import os.path
import os
import datetime

def diff_date(pub_date, ds):
    if pub_date:
        result = [x.days for x in ds - np.repeat(pub_date, len(ds))]
    else:
        result = ds
    
    return result

def guiyihua(data, ratio = 1):
    max_data = data.max()
    min_data = data.min()
    return ratio * (data - min_data)/(max_data - min_data)


class PiaoFangAnalyze:

    def __init__(self, dirname, film_name, pub_date=None):
        self.pub_date = pub_date
        self.film_name = os.path.basename(dirname)

        self.baidu_fname = dirname + os.path.sep + 'baidu_index.xls'
        self.douban_fname = dirname + os.path.sep + 'douban_film_score.xls'
        self.gewara_fname = dirname + os.path.sep + 'gewara.xls'
        self.piaofang_history_fname = dirname + os.path.sep + \
                'piaofang168_history.xls'
        self.piaofang_realtime_fname = dirname + os.path.sep + \
                'piaofang168_realtime.xls'
        self.film_name = film_name

        self.init_baidu_index()
        self.init_douban_comment()
        self.init_gewara_data()
        self.init_piaofang_history_data()
    

    def init_baidu_index(self):
        try:
            temp = read_excel(self.baidu_fname)
        except IOError as msg:
            print(e)
            return None
    
        ds = [x.date() for x in temp['收集时间']]
        temp.index = diff_date(self.pub_date, ds)

        self.baidu_f = temp.drop(['内部编号','搜索类型','搜索排名',
            '搜索趋势','收集时间','更新时间'], axis=1).groupby(level=0).max()
        

    def init_douban_comment(self):
        try:
            temp = read_excel(self.douban_fname)
        except IOError as e:
            print(e)
            return None
    
        ds = np.array([x.date() for x in temp['收集时间']])
        temp.index = diff_date(self.pub_date, ds)

        self.douban_f = temp.drop(['内部编号','豆瓣编号',
            '收集时间','更新时间'], axis = 1)


    def init_gewara_data(self):
        try:
            temp = read_excel(self.gewara_fname)
        except IOError as e:
            print(e)
            return None

        ds = [x.date() for x in temp['收集时间']]
        temp.index = diff_date(self.pub_date, ds)

        self.gewara_f = temp.drop(['内部编号', '格瓦拉编号', 
            '收集时间', '更新时间'], axis=1).groupby(level=0).max()


    def init_piaofang_history_data(self):
        try:
            temp = read_excel(self.piaofang_history_fname)
        except IOError as e:
            print(e)
            return None

        ds = [x.date() for x in temp['发布时间']]
        temp.index = diff_date(self.pub_date, ds) 
    
        self.piaofang_h = temp.drop(['内部编号','发布时间','收集时间',
            '更新时间'], axis=1).groupby(level=0).max()
    
    
    def plot_index(self,outfilename = None, start =0, stop = 20):
        fig = plt.figure()
        ax = fig.add_subplot(2,1,1)

        ax1 = ax.twinx()
        ax1.plot(self.baidu_f.index, 
                guiyihua(self.baidu_f['搜索指数']) * 100,
                label = '百度搜索指数',
                linewidth= 1.5)
        ax1.plot(self.douban_f.index, 
                guiyihua(self.douban_f['评价人数增量']) * 100, 
                label = '评价指数',
                linewidth = 1.5)
        ax1.plot(self.gewara_f.index,
                guiyihua(self.gewara_f['购买人数增量']) * 100, 
                label = '购买指数',
                linewidth = 1.5)

        ax1.set_xlim(start, stop)
        ax.set_xlim(start, stop)

        dates = [ piaofang.pub_date + datetime.timedelta(x) 
                for x in self.piaofang_h.index]
        colors = ['c' if x.weekday()== 5 or x.weekday() == 6 else 'm'
                for x in dates]

        ax.bar(self.piaofang_h.index, 
                self.piaofang_h['今日票房/万'],
                label = '今日票房',
                color = colors)


        ax.set_ylabel('今日票房')
        
        ax1.legend(loc = 'upper right',fontsize ='small')

        ax2 = fig.add_subplot(2,1,2)
        ax2.plot(self.piaofang_h.index,
                self.piaofang_h['今日排片/%'],
                linewidth = 1.5)
        ax2.set_xlim(start, stop)
        ax2.set_xlabel('上映天数')
        ax2.set_ylabel('今日排片占比(%)')

        ax.set_title(self.film_name)
        
        if outfilename:
            fig.savefig(outfilename, dpi=100)
    
    
    def plot_pingfen(self, outfilename = None, start=0, stop=20):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax1 = ax.twinx()

        dates = [ piaofang.pub_date + datetime.timedelta(x) 
                for x in self.piaofang_h.index]
        colors = ['c' if x.weekday()== 5 or x.weekday() == 6 else 'm'
                for x in dates]

        ax.bar(self.piaofang_h.index, 
                self.piaofang_h['今日票房/万'],
                label = '今日票房',
                color = colors)
        
        ax1.plot(self.gewara_f.index, self.gewara_f['电影评分'],
                label = '格瓦拉评分', linewidth=1.5)
        ax1.plot(self.douban_f.index, self.douban_f['电影评分'],
                label = '豆瓣评分', linewidth=1.5)

        ax.set_xlim(start, stop)
        ax1.set_xlim(start, stop)

        ax1.legend(loc = 'upper right')

        ax.set_title(self.film_name)
        ax.set_xlabel('上映天数')

        if(outfilename):
            fig.savefig(outfilename)


if __name__ == '__main__':
    # 首先将windows下的微软亚黑字体文件msyh.ttf拷贝到用户目录下的.fonts目录下
    fontManager.defaultFont['ttf']='~/.fonts/msyh.ttf'
    matplotlib.rcParams['font.sans-serif']=['Microsoft YaHei']
    matplotlib.rcParams['font.family']=['sans-serif']

    # 指定电影名
    film_name = '匆匆那年'

    # 指定电影首映日期
    pub_date = pd.datetime(2014,12,5).date()

    # 指定抓取数据的存储目录的上一级目录，电影名称自动加上
    dirname = r'/home/lxq/python/2014-12-25 02.51.02.786234/'+film_name

    # 初始化一个PiaoFangAnalyze对象
    piaofang = PiaoFangAnalyze(dirname, film_name, pub_date)

    # 画出票房与相关指数的关系
    piaofang.plot_index(film_name + '.png')

    # 画出票房与相关评分的关系, 会自动将画完的图存储为PNG图片，也可以是SVG的
    piaofang.plot_pingfen(film_name+'_p.png')

    # 如果是交互式的可以显示出图形来
    plt.show()


