# -*- coding: utf-8 -*-

# Scrapy settings for ourku project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'ourku'

SPIDER_MODULES = ['ourku.spiders']
NEWSPIDER_MODULE = 'ourku.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ourku (+http://www.yourdomain.com)'
ITEM_PIPELINES = {'ourku.pipelines.OurkuPipeline':300}

LOG_LEVEL = 'INFO'
