# -*- coding: utf-8 -*-

# Scrapy settings for REI project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'REI'
SPIDER_MODULES = ['REI.spiders']
NEWSPIDER_MODULE = 'REI.spiders'
DOWNLOAD_DELAY = 0.0
COOKIES_ENABLED = False
CONCURRENT_REQUESTS = 100
CONCURRENT_REQUESTS_PER_DOMAIN = 100
AUTOTHROTTLE_ENABLED = False

FEED_EXPORTERS = {
        'sqlite': 'scripts.exporters.SqliteItemExporter',
    }

ITEM_PIPELINES = {
    'REI.pipelines.SQLPipeline': 300,
}

### More comprehensive list can be found at 
### http://techpatterns.com/forums/about304.html
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0) Gecko/16.0 Firefox/16.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10',
    'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
    'Mozilla/5.0 (compatible; MSIE 9.0; AOL 9.7; AOLBuild 4343.19; Windows NT 6.1; WOW64; Trident/5.0; FunWebProducts)'
]
HTTP_PROXY = 'http://127.0.0.1:8123'

#Squid Proxies
#ACCT:45099
PROXIES = [
    #{'ip_port': '173.234.165.60:8800', 'user_pass': ''},#B
    #{'ip_port': '173.234.165.77:8800', 'user_pass': ''},#B
    #{'ip_port': '89.47.28.226:8800', 'user_pass': ''},#B
    #{'ip_port': '206.214.93.182:8800', 'user_pass': ''},#B
    #{'ip_port': '206.214.93.5:8800', 'user_pass': ''},#B
    {'ip_port': '89.47.28.220:8800', 'user_pass': ''},#B
    #{'ip_port': '173.234.165.182:8800', 'user_pass': ''},#B
    #{'ip_port': '50.31.10.114:8800', 'user_pass': ''},#B
    #{'ip_port': '173.234.165.175:8800', 'user_pass': ''},#B
    #{'ip_port': '50.31.10.106:8800', 'user_pass': ''},#B
        ]

DOWNLOADER_MIDDLEWARES = {
    #'REI.middlewares.RandomUserAgentMiddleware': 400,
    #'REI.middlewares.ProxyMiddleware': 410,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    
    #TO DISABLE PROXIES ->Comment out HttpProxyMiddleware and RandomProxyMiddleware
    #'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
    #'REI.middlewares.RandomProxyMiddleware': 100,
    #Disable compression middleware, so the actual HTML pages are cached
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'REI (+http://www.yourdomain.com)'
