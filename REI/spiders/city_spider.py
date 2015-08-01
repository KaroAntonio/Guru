import scrapy
import time
import datetime
import re
import json
from processCities import gen_city_urls
from parse import parse_house_response
from parse import parse_taxes_response
from parse import parse_price_response
from bs4 import BeautifulSoup
from crawl import gen_urls
from random import randint
from scrapy.http.request import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from REI.items import CityItem

class CitySpider(scrapy.Spider):
    name = "city"
    allowed_domains = ["city-data.com"]
    start_urls =[
        'http://www.city-data.com/city/Seguin-Texas.html',
        'http://www.city-data.com/city/Houston-Texas.html',
        'http://www.city-data.com/city/Rockdale-Texas.html',
    ]
    
    def __init__(self, *args, **kwargs):
        super(CitySpider, self).__init__(*args, **kwargs)
        self.start_urls = gen_city_urls()
            
    def set_crawler(self, crawler):
        super(CitySpider, self).set_crawler(crawler)
        crawler.settings.overrides['ITEM_PIPELINES'] = {}
        crawler.settings.overrides['DOWNLOAD_DELAY'] = 2
        
    def parse(self,response):
        #wait a random amount of time to disguise spider
        city = CityItem()
        try:
            city['pop_growth'] = re.search(r'([/+,-].*)%',response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " city-population ")]/text()').extract()[1]).group(1)
        except:
            city['pop_growth'] = None
            print('No Pop Growth Data')
            
        city['city'] = re.search(r'(.*):',response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " hgraph ")]/table/tr/td/b/text()').extract()[0]).group(1)
        city['state'] = re.search(r'(.*):',response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " hgraph ")]/table/tr/td/b/text()').extract()[1]).group(1) 
        
        yield city
            