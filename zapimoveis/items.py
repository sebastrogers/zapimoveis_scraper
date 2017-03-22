# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class ZapItem(Item):
    # Extraídos do Json
    id = Field()
    name = Field()
    action = Field()
    type = Field()
    country = Field()
    city = Field()
    state = Field()
    postal_code = Field()
    street = Field()
    description = Field()
    latitude = Field()
    longitude = Field()
    url = Field()
    price = Field()
    currency = Field()
    seller_type = Field()
    seller_name = Field()
    seller_url = Field()
    client_code = Field()
    transaction = Field()
    property_subtype = Field()

    # Extraídos do Html
    bedrooms = Field()
    suites = Field() # buscar tradução
    useful_area_m2 = Field()
    total_area_m2 = Field()
    vacancies = Field()

    def __repr__(self):
        return self['name']
