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
from random import randint
from scrapy.http.request import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from REI.items import HouseItem

class HouseSpiderSpider(scrapy.Spider):
    name = "house"
    allowed_domains = ["zillow.com"]
    visited = True
    #zestimate err
    #start_urls = ( 'http://www.zillow.com/homedetails/305-E-5th-St-Bowie-AZ-85605/2102017608_zpid/',)
    #lot size err  FIXED
    #start_urls = ( 'http://www.zillow.com/homedetails/9151-W-Greenway-Rd-UNIT-204-Peoria-AZ-85381/7922598_zpid/',)
    #state err
    #start_urls = ( 'http://www.zillow.com/homedetails/370-Montague-Dr-Bandera-TX/90265423_zpid/',)
    #community house FIXED
    #start_urls = ( 'http://www.zillow.com/community/coldwater-ranch/2112804733_zpid/',)
    #Traceback Err 
    #start_urls = ( 'http://www.zillow.com/homedetails/5145-W-Sanna-St-Glendale-AZ-85302/7734624_zpid/',)
    #No City 
    #start_urls = ( 'http://www.zillow.com/homedetails/2-Kardamena-Out-Of-Area-Town-Gr-85302/2103161700_zpid/',)
    #Tax Err?
    start_urls = ( 'http://www.zillow.com/homedetails/236-Leland-Creek-Cir-Winter-Park-CO-80482/2104158017_zpid/',)
    #good listing
    #start_urls = ( 'http://www.zillow.com/homedetails/9944-W-Ocotillo-Dr-Sun-City-AZ-85373/8094905_zpid/',)
    
    def __init__(self, url=None, *args, **kwargs):
        super(HouseSpiderSpider, self).__init__(*args, **kwargs)
    
    def parse(self,response):
        #wait a random amount of time to disguise spider
        return parse_house_response(self, response)
        
    def parse_history(self,response):
        #Parse Price History Table
        return parse_price_response(self, response)
        
    def parse_taxes(self,response):
        #Parse Tax History Table
        yield parse_taxes_response(self, response)
            