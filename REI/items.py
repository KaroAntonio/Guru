# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class HouseItem(scrapy.Item):
    id = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    price = scrapy.Field()
    sale_status = scrapy.Field()
    rent_zestimate = scrapy.Field()
    zestimate = scrapy.Field()
    mortgage_estimate = scrapy.Field()
    lot_size = scrapy.Field()
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    sqrft = scrapy.Field()
    lot_size = scrapy.Field()
    timestamp = scrapy.Field()
    zillow_url = scrapy.Field()
    tax_url = scrapy.Field()
    features = scrapy.Field()
    description = scrapy.Field()
    facts = scrapy.Field()
    price_history = scrapy.Field()
    tax_history = scrapy.Field()
    rental_valuation = scrapy.Field()
    valuation = scrapy.Field()
    notes = scrapy.Field()
    latlong = scrapy.Field()
    sqlite_keys = []
    
class CityItem(scrapy.Item):
    city = scrapy.Field()
    state = scrapy.Field()
    pop_growth = scrapy.Field()
