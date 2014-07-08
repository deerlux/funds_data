#!/usr/bin/python
# coding=UTF-8
"""
练习网络抓取程序，将dive into python3的中文版抓取下来。
"""
from BeautifulSoup import BeautifulSoup as bp
import urllib2

if __name__ == "__main__":
    _url = 'http://woodpecker.org.cn/diveintopython3/'
    index_html = urllib2.urlopen(_url).read()
    soup = bp(index_html)
    hrefs = [link.get('href') for link in soup.findAll('a')]
    print(hrefs)
    hrefs = [x for x in hrefs if str(x).endswith('.html')]
    print(hrefs)


        

