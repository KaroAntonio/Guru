# -*- coding: utf-8 -*-
import scrapy
import time
import re
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from REI.items import HouseItem

class ZillowSpiderSpider(CrawlSpider):
    name = "zillow"
    allowed_domains = ["zillow.com"]
    visited = True
    start_urls = ( 'http://www.zillow.com/homes/for_sale/AZ/fsba,fsbo,new_lt/house,condo,apartment_duplex,townhouse_type/8_rid/days_sort/33.650172,-112.067113,33.599071,-112.157235_rect/13_zm/0_mmm/',
    )
    
    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        
        #Once a link is visited, do not follow it again
        Rule(LinkExtractor(allow=('/homes.*?_p/', ), deny=('subsection\.php', )), follow=visited),

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(allow=('/homedetails/', )), callback='parse_house'),
    )
    
    def parse_house(self,response):
        
        house = HouseItem()
        house['zillow_url'] = response.url
        house['address'] =  re.search( r'^(.*?),',response.xpath('//h1/text()').extract()[0] ).group(1)
        house['city'] = re.search( r'^(.*?),', response.xpath('//h1/span/text()').extract()[0] ).group(1)
        house['state'] = re.search( r',\s(.*?)\s', response.xpath('//h1/span/text()').extract()[0] ).group(1)
        non_decimal = re.compile(r'[^\d.]+')
        house['price'] = non_decimal.sub('', response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " main-row ")]/span/text()').extract()[0].replace(r'$', "").replace(r',', "").replace( "[^\\d]", "" ) )
        house['sale_status'] = response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " status-icon-row ")]/text()').extract()[1]
        house['rent_zestimate'] = re.search( r'^(.*?)/', response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " zest-value ")]/text()').extract()[1] ).group(1).replace(r',', "").replace(r'$', "")
        house['bedrooms'] = re.search( r'^(.*?)\s', response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " addr_bbs ")]/text()').extract()[0] ).group(1)
        house['bathrooms'] = re.search( r'^(.*?)\s', response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " addr_bbs ")][2]/text()').extract()[0] ).group(1)
        house['sqrft'] = re.search( r'^(.*?)\s', response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " addr_bbs ")][3]/text()').extract()[0] ).group(1).replace(r',', "")
        house['lot_size'] = re.search( r'\s(.*?)$', response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " zsg-list_square ")]/li[1]/text()').extract()[0] ).group(1).replace(r',', "")
        house['zpid'] = re.search(r'/(\d*)_zpid', response.url).group(1)
        house['date_scraped'] = time.strftime("%d/%m/%Y")
        yield house
