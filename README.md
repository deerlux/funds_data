funds_data
==========

抓取网上的基金数据，将数据存储到本地的mysql或postgresql数据库中。

主要通过两个类:OurkuFundsInfoFetcher、FundsDataDB以及get_funds_data.py中的几个函数来实现。

get_funds_data.get_jrj_data(data_date)
----------

从 http://www.jrj.com.cn 网站上抓取基金净值数据。

函数：get_funds_data.get_ourku_data(data_date)
--------

从 http://www.ourku.com 网站上抓取基金净值数据。

函数：get_funds_data.data2db_simple(conn, funds)
--------

将抓取的净值数据写入数据库，利用DBAPI的方式操作数据库，速度较快。

函数：get_funds_data.data2db(engine, funds)
--------

将抓取的净值数据写入数据库，利用sqlalchemy操作数据库，插入数据速度较慢。

类：FundsDataDB
--------

以ORM的方式访问数据库的接口类。

类：OurkuFundsInfoFetcher
--------

从 http://www.ourku.com 网站抓取基金持仓、基金份额、基金类型等基础信息的类库。

test.py
--------

抓取基础信息并入库存储的试验程序。



