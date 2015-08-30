import scrapy
import time
import datetime
import re
import json
from REI.scraper import get_ajax_url
from REI.scraper import get_price_history
from bs4 import BeautifulSoup
from REI.crawl import gen_urls
from random import randint
from scrapy.http.request import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from REI.items import HouseItem

class ZillowSpiderSpider(CrawlSpider):
    name = "zillow"
    allowed_domains = ["zillow.com"]
    visited = True
    requests = 0
    max_interval = 10
    request_interval = 10
    pauseEnabled = False;
    
    start_urls = ( 'http://www.zillow.com/homes/for_sale/AZ/fsba,fsbo,new_lt/house,condo,apartment_duplex,townhouse_type/8_rid/days_sort/33.643688,-112.216523,33.61814,-112.261584_rect/14_zm/0_mmm/',
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
    
    def __init__(self, url=None, prll=False, *args, **kwargs):
        super(ZillowSpiderSpider, self).__init__(*args, **kwargs)
        if (prll):
            self.start_urls = [ url ]
        else:
            self.start_urls = gen_urls(url)
        
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
        zestimate_field = response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " zest-value ")]/text()').extract()[1]
        if (zestimate_field != 'Unavailable'):
            house['rent_zestimate'] = re.search( r'^(.*?)/', zestimate_field ).group(1).replace(r',', "").replace(r'$', "")
        else:
            house['rent_zestimate'] = -1;
            
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
        house['id'] = re.search(r'/(\d*)_zpid', response.url).group(1)
        #https://docs.python.org/2/library/datetime.html
        house['timestamp'] = datetime.datetime.now().isoformat()
        
        #Request Histories
        soup = BeautifulSoup(response.body)
        history_url = get_ajax_url(soup, "z-hdp-price-history")
        tax_url = get_ajax_url(soup, "z-expando-table")
        history_request = Request(history_url, 
                          callback=self.parse_history)
        history_request.meta['item'] = house
        history_request.meta['tax_url'] = tax_url
        house['tax_url'] = tax_url
        
        return history_request
        
    def parse_history(self,response):
        #Parse Price History Table
        house = response.meta['item']
        tax_url = house['tax_url']
        price_history = []
        pattern = r' { "html": "(.*)" }'
        html = re.search(pattern, response.body).group(1)
        html = re.sub(r'\\"', r'"', html)  # Correct escaped quotes
        html = re.sub(r'\\/', r'/', html)  # Correct escaped forward
        if (html != ""):
            soup = BeautifulSoup(html)
            table = soup.find('table')
            table_body = table.find('tbody')
            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele for ele in cols]
                cols = cols[:3]
                if (cols[2].find('span') != None):
                    date = cols[0].get_text()
                    event = cols[1].get_text()
                    price = cols[2].find('span').get_text()
                    price_history.append([date, event, price])
            #Store history as JSON string    
            house['price_history'] = json.dumps(price_history)
        tax_request = Request(tax_url, 
                          callback=self.parse_taxes)
        tax_request.meta['item'] = house
        
        return tax_request
        
    def parse_taxes(self,response):
        #Parse Tax History Table
        house = response.meta['item']
        tax_history = []
        pattern = r' { "html": "(.*)" }'
        html = re.search(pattern, response.body).group(1)
        html = re.sub(r'\\"', r'"', html)  # Correct escaped quotes
        html = re.sub(r'\\/', r'/', html)  # Correct escaped forward
        if (html != "") :
            soup = BeautifulSoup(html)
            table = soup.find('table')
            table_body = table.find('tbody')
            rows = table_body.find_all('tr')
            for row in rows:
                try:
                    cols = row.find_all('td')
                    cols = [ele for ele in cols]
                    date = cols[0].get_text()
                    tax = cols[1].contents[0]
                    assessment = cols[3].get_text()
                    tax_history.append([date, tax, assessment])
                except:
                    tax_history.append([Error])
            house['tax_history'] = json.dumps(tax_history)
            
        yield house