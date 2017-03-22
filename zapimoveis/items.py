# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZapItem(scrapy.Item):
    # Extraídos do Json
    action = scrapy.Field()
    id = scrapy.Field()
    type = scrapy.Field()
    country = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    postal_code = scrapy.Field()
    street = scrapy.Field()
    description = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    seller_type = scrapy.Field()
    seller_name = scrapy.Field()
    seller_url = scrapy.Field()
    client_code = scrapy.Field()
    transaction = scrapy.Field()
    property_subtype = scrapy.Field()

    # Extraídos do Html
    bedrooms = scrapy.Field()
    suites = scrapy.Field() # buscar tradução
    useful_area_m2 = scrapy.Field()
    total_area_m2 = scrapy.Field()
    vacancies = scrapy.Field()

    def __repr__(self):
        return self['name']
