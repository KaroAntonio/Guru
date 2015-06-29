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
from crawl import div_url
from random import randint
from scrapy.http.request import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from REI.items import HouseItem

class MapSpiderSpider(CrawlSpider):
    name = "map"
    allowed_domains = ["zillow.com"]
    visited = True
    initialized = False
    requests = 0
    max_interval = 10
    request_interval = 10
    pauseEnabled = False;
    
    start_urls = ( 'http://www.zillow.com/homes/for_sale/CA/fsba,fsbo,new_lt/house,condo,apartment_duplex,townhouse_type/9_rid/days_sort/35.637209,-114.590149,32.382281,-120.357971_rect/7_zm/0_mmm/',
    )
    
    rules = (
        # Extract links matching 'homes' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        
        #Once a link is visited, do not follow it again
        Rule(LinkExtractor(allow=('/homes.*?_p/', ), deny=('subsection\.php', )), follow=visited, ),

        # Extract links matching 'homedetails' and parse them with the spider's method parse_house
        Rule(LinkExtractor(allow=('/homedetails/', )), callback='parse_house'),
        Rule(LinkExtractor(allow=('/community/', )), callback='parse_house'),
    )
    
    def __init__(self, url=None, *args, **kwargs):
        super(MapSpiderSpider, self).__init__(*args, **kwargs)
        #self.start_urls = gen_urls(url)
    
    def parse_start_url(self,response):
        if (self.initialized == False):
            self.initialized = True
            print("Parse Start")
            return self.parse_map(response);
        else:
            return
        
    def parse_map(self,response):
        # check if map returns over twenty pages
        pageEls = response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " zsg-pagination ")]/li/a/text()').extract()
        if (len(pageEls) == 7):
            #there are more than 5 or 6 pages
            if (pageEls[5] != '20'):
                print("<20 Pages, Parse Map: " + response.url);
                parse_request = Request(response.url, 
                          callback=self.parse)
                yield parse_request;
            else:
                print("Subdivide Map: " + response.url);
                urls = div_url(response.url,2)
                for u in urls:
                    sub_request = Request(u, 
                          callback=self.parse_map, dont_filter=True)
                    yield sub_request;
        else:
            #parse page
            print("<6 Pages, Parse Map: " + response.url)
            parse_request = Request(response.url, 
                      callback=self.parse)
            yield parse_request;
        return
       
    def link_callback(self,response):
        #somehow couldnt remove this to another function
        self.requests += 1
        if (self.pauseEnabled & (self.requests % self.request_interval == 0)):
            print("Pause")
            self.request_interval = randint(0,self.max_interval)
            pause_time = randint(0,200)/100
            time.sleep(pause_time)
            print("Paused " + str(pause_time) + "s")
    
    def parse_house(self,response):
        #wait a random amount of time to disguise spider
        #time.sleep(randint(0,50)/100)
        self.requests += 1
        if (self.pauseEnabled & (self.requests % self.request_interval == 0)):
            print("Pause")
            self.request_interval = randint(1,self.max_interval)
            pause_time = randint(0,200)/100
            time.sleep(pause_time)
            print("Paused " + str(pause_time) + "s")
        
        #Parse House 
        return parse_house_response(self, response)
        
    def parse_history(self,response):
        #Parse Price History Table
        return parse_price_response(self, response)
        
    def parse_taxes(self,response):
        #Parse Tax History Table
        yield parse_taxes_response(self, response)