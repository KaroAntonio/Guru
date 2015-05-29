# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class HouseItem(scrapy.Item):
    zpid = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    price = scrapy.Field()
    sale_status = scrapy.Field()
    rent_zestimate = scrapy.Field()
    mortgage_estimate = scrapy.Field()
    lot_size = scrapy.Field()
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    sqrft = scrapy.Field()
    lot_size = scrapy.Field()
    date_scraped = scrapy.Field()
    zillow_url = scrapy.Field()
