import scrapy
import time
import datetime
import re
import json
from parse import parse_house_response
from parse import parse_taxes_response
from parse import parse_price_response
from scraper import get_ajax_url
from scraper import get_price_history
from bs4 import BeautifulSoup
from crawl import gen_urls
from random import randint
from scrapy.http.request import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from REI.items import HouseItem

class ExpertSpiderSpider(scrapy.Spider):
    name = "expert"
    allowed_domains = ["finestexpert.com"]
    start_urls = ( 'http://www.finestexpert.com/Investment-Property/For-Sale/2698%20N%2043rd%20Ave%20APT%20C,%20Green%20Valley%20AZ?beds=1&baths=1.5&sqft=1000&propertytype=Condo&asking=27000',)
    
    def __init__(self, url=None, *args, **kwargs):
        super(ExpertSpiderSpider, self).__init__(*args, **kwargs)
    
    def parse(self,response):
        #wait a random amount of time to disguise spider
        #print(response.body)
        return
            