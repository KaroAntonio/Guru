import time
import datetime
import re
import json
from bs4 import BeautifulSoup
from random import randint

from crawl import gen_urls
from scraper import get_ajax_url
from scraper import get_price_history

import scrapy
from scrapy.http.request import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from REI.items import HouseItem

def parse_house_response(self, response):
    house = HouseItem()
    house['zillow_url'] = response.url
    address_field = response.xpath('//h1/text()').extract()[0]
    address_test = re.search( r'^(.*?),', address_field )
    if (address_test == None):
        house['address'] = address_field
    else:
        house['address'] = address_test.group(1)
    city_field = re.search( r'^(.*?),', response.xpath('//h1/span/text()').extract()[0] )
    if (city_field != None):
        house['city'] = city_field.group(1)
    else:
        house['city'] = None
    house['description'] = response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " zsg-content-component ")]/div/text()').extract()[0]
    state_field = re.search( r',\s(.{2})\s?', response.xpath('//h1/span/text()').extract()[0] )
    if (state_field != None):
        house['state'] = state_field.group(1)
    else:
        house['state'] = None
    non_decimal = re.compile(r'[^\d.]+')
    house['price'] = non_decimal.sub('', response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " main-row ")]/span/text()').extract()[0].replace(r'$', "").replace(r',', "").replace( "[^\\d]", "" ) )
    house['sale_status'] = response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " status-icon-row ")]/text()').extract()[1].lstrip().rstrip()
    stripped_line = house['sale_status'].strip()
    if (stripped_line == ""):
        house['sale_status'] = response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " status-icon-row ")]/span/text()').extract()[0]
    fact_fields = response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " fact-group-container ")]/ul/li/text()').extract();
    if fact_fields:
        house['facts'] = json.dumps(fact_fields)
    rent_zestimate_field = response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " zest-value ")]/text()').extract()[1]
    if (rent_zestimate_field != 'Unavailable'):
        house['rent_zestimate'] = re.search( r'^(.*?)/', rent_zestimate_field ).group(1).replace(r',', "").replace(r'$', "")
    else:
        house['rent_zestimate'] = -1;
    zestimate_field = response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " zest-value ")]/text()').extract()[0]
    if (zestimate_field != 'Unavailable'):
        house['zestimate'] = zestimate_field.replace(r',', "").replace(r'$', "")
    else:
        house['zestimate'] = -1;

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

def parse_price_response(self, response):
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
            if ((len(cols) >= 3) and cols[2].find('span') != None):
                date = cols[0].get_text()
                event = cols[1].get_text()
                price = cols[2].find('span').get_text()
                price_history.append([date, event, price])
        #Store history as JSON string    
        house['price_history'] = json.dumps(price_history)
    tax_request = Request(tax_url, 
                      callback=self.parse_taxes)
    tax_request.meta['item'] = house
    return tax_request;

def parse_taxes_response(self, response):
        
    house = response.meta['item']
    
    house['tax_url'] = '';
    tax_history = []
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
        
    return evaluate_house(house)

def evaluate_house(house):
    #Valuate House based on available information
    #Perform Projection
    rental_income = float(house['rent_zestimate']) #monthly
    price = float(house['price']) #current
    appreciation = 0.04 #annual
    inflation = 0.03 #annual
    timeframe = 15 #years
    current_taxes = 0
    
    try:
        tax_history = json.loads(house['tax_history'])
        current_taxes = float(tax_history[0][1].replace(r',', "").replace(r'$', ""))
    except:
        #if there is no tax info available, assume a bad tax rate
        current_taxes = price * 0.0185
    
    #ASSUMING
    #house paid in cash
    #constant inflation and property appreciation
    #no utilities
    #no income tax
    net_income = 0
    for i in range(0, 15):
        #subtract 
        #Mortgage Payments, HOA, Variable Upkeep Costs, vacancy, mgmt costs, income tax
        #add 
        #tax deductibles
        net_income += rental_income * pow((1 + inflation),i) * 12
        net_income -= current_taxes * pow((1 + appreciation),i) 
        if hasattr(house, 'HOA'):
            print house['HOA']
    
    house['rental_valuation'] = net_income/price
    
    return house;
        
    
    
