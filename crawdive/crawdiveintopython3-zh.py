#!/usr/bin/python
# coding=UTF-8
"""
练习网络抓取程序，将dive into python3的中文版抓取下来。
"""
from bs4 import BeautifulSoup as bp
import urllib2

if __name__ == "__main__":
    _url = 'http://woodpecker.org.cn/diveintopython3/'
    index_html = urllib2.urlopen(_url).read()
    soup = bp(index_html)
    hrefs = [link.get('href') for link in soup.find_all('a')]
    # print(hrefs)
    hrefs1 = [str(x) for x in hrefs]
    # html_filter = lambda x: x.endswith('html')
    hrefs1 = [x for x in hrefs1 if x.endswith('.html')]
    print('\n'.join(hrefs1))
    


        

