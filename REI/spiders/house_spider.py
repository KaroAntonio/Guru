import scrapy
import time
import datetime
import re
from zillow_spider import ZillowSpiderSpider
from crawl import gen_urls
from random import randint
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from REI.items import HouseItem

class HouseSpiderSpider(scrapy.Spider):
    name = "house"
    allowed_domains = ["zillow.com"]
    visited = True
    #lot size err
    #start_urls = ( 'http://www.zillow.com/homedetails/9151-W-Greenway-Rd-UNIT-204-Peoria-AZ-85381/7922598_zpid/',)
    #address err
    #start_urls = ( 'http://www.zillow.com/homedetails/(Undisclosed-Address)-Sun-City-AZ-85375/2106415148_zpid/',)
    #community house
    start_urls = ( 'http://www.zillow.com/community/coldwater-ranch/2112804733_zpid/',)
    #good listing
    #start_urls = ( 'http://www.zillow.com/homedetails/9944-W-Ocotillo-Dr-Sun-City-AZ-85373/8094905_zpid/',)
    
    def __init__(self, url=None, *args, **kwargs):
        super(HouseSpiderSpider, self).__init__(*args, **kwargs)
        
    
    def parse(self,response):
        #wait a random amount of time to disguise spider
        
        house = HouseItem()
        house['zillow_url'] = response.url
        address_field = response.xpath('//h1/text()').extract()[0]
        address_test = re.search( r'^(.*?),', address_field )
        if (address_test == None):
            house['address'] = address_field
        else:
            house['address'] = address_test.group(1)
        house['city'] = re.search( r'^(.*?),', response.xpath('//h1/span/text()').extract()[0] ).group(1)
        house['state'] = re.search( r',\s(.*?)\s', response.xpath('//h1/span/text()').extract()[0] ).group(1)
        non_decimal = re.compile(r'[^\d.]+')
        house['price'] = non_decimal.sub('', response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " main-row ")]/span/text()').extract()[0].replace(r'$', "").replace(r',', "").replace( "[^\\d]", "" ) )
        house['sale_status'] = response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " status-icon-row ")]/text()').extract()[1].lstrip().rstrip()
        stripped_line = house['sale_status'].strip()
        if (stripped_line == ""):
            house['sale_status'] = response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " status-icon-row ")]/span/text()').extract()[0]
        house['rent_zestimate'] = re.search( r'^(.*?)/', response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " zest-value ")]/text()').extract()[1] ).group(1).replace(r',', "").replace(r'$', "")
        bedroom_field = re.search( r'^(.*?)\s', response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " addr_bbs ")]/text()').extract()[0] )
        if (bedroom_field != None): 
            house['bedrooms'] = bedroom_field.group(1)
        else:
            house['bedrooms'] = "Studio"
        house['bathrooms'] = re.search( r'^(.*?)\s', response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " addr_bbs ")][2]/text()').extract()[0] ).group(1)
        house['sqrft'] = re.search( r'^(.*?)\s', response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " addr_bbs ")][3]/text()').extract()[0] ).group(1).replace(r',', "")
        lot_field = response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " zsg-list_square ")]/li[1]/text()').extract()[0]
        lot_field_test = re.search( r'^([^0-9]*)$', lot_field)
        if (lot_field_test != None):
            house['lot_size'] = lot_field
        else:
            house['lot_size'] = re.search( r'\s(.*?)$', lot_field ).group(1).replace(r',', "")
        house['zpid'] = re.search(r'/(\d*)_zpid', response.url).group(1)
        #https://docs.python.org/2/library/datetime.html
        house['timestamp'] = datetime.datetime.now().isoformat()
        yield house