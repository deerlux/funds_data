#!/usr/bin/python
# coding=UTF-8
"""
练习网络抓取程序，将dive into python3的中文版抓取下来。
"""
from bs4 import BeautifulSoup as BS
import urllib2
from ConfigParser import ConfigParser
import os.path

if __name__ == "__main__":
    _url = 'http://woodpecker.org.cn/diveintopython3/'
    
    conf = ConfigParser()
    conf.read('crawdiveintopython3-zh.conf')
    save_dir = conf.get('main','save_dir')

    index_html = urllib2.urlopen(_url).read()

#   save html to file index.html
    file1 = open(os.path.join(save_dir, 'index.html'), 'w')
    file1.write(index_html)
    file1.close()

#   parse the html file
    soup = BS(index_html)

    hrefs = [str(link.get('href')) for link in soup.find_all('a')]
    hrefs_file = [x for x in hrefs if x.endswith('.html')]
    #print('\n'.join(hrefs_file))

    for x in hrefs_file:
        html = urllib2.urlopen(_url + x).read()

        file1 = open(os.path.join(save_dir, x),'w')
        file1.write(html)
        file1.close()

        print("%s\t\t file writing finished!" % x)


