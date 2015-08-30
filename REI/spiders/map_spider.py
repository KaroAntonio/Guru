import scrapy
import time
import datetime
import re
import json
from REI.parse import parse_house_response
from REI.parse import parse_taxes_response
from REI.parse import parse_price_response
from REI.scraper import get_ajax_url
from REI.scraper import get_price_history
from bs4 import BeautifulSoup
from REI.crawl import gen_urls
from REI.crawl import div_url
from random import randint
from random import uniform
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
    request_interval_range = [1000,2000]
    request_interval = request_interval_range[0]
    pause_range = [(5*60),(10*60)]
    pauseEnabled = True;
    
    #Make sure the URL comes from the state view of the map (or listings are loaded dynamically)
    start_urls = ( 'http://www.zillow.com/homes/for_sale/NM/41_rid/37.396346,-100.255738,30.902224,-111.791382_rect/6_zm/',
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
        
    def pause(self):
        self.requests += 1
        if (self.pauseEnabled & (self.requests % self.request_interval == 0)):
            print("Pause")
            self.request_interval = randint(
                self.request_interval_range[0],
                self.request_interval_range[1])
            pause_time = uniform(self.pause_range[0],self.pause_range[1])
            time.sleep(pause_time)
            print("Paused " + str(pause_time) + "s")
    
    def parse_start_url(self,response):
        if (self.initialized == False):
            self.initialized = True
            print("Parse Start")
            return self.parse_map(response);
        else:
            return
        
    def parse_map(self,response):
        # check if map returns over twenty pages
        self.pause()
        pageEls = response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " zsg-pagination ")]/li/a/text()').extract()
        if (len(pageEls) == 7):
            #if there are less than 20 pages
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
        self.pause()
    
    def parse_house(self,response):
        #Parse House 
        self.pause()
        return parse_house_response(self, response)
        
    def parse_history(self,response):
        #Parse Price History Table
        self.pause()
        return parse_price_response(self, response)
        
    def parse_taxes(self,response):
        #Parse Tax History Table
        self.pause()
        yield parse_taxes_response(self, response)