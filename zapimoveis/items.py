# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

#       {'@context': 'https://schema.org',
#        '@type': 'BuyAction',
#        'object': {'@id': '#12764639Venda',
#         '@type': 'SingleFamilyResidence',
#         'address': {'addressCountry': {'@type': 'Country', 'name': 'BR'},
#          'addressLocality': 'RECIFE',
#          'addressRegion': 'PE',
#          'postalCode': '52000000',
#          'streetAddress': 'Casa Amarela, Recife - PE'},
#         'description': '2 quartos | 52m<sup>2</sup> | 1 vaga',
#         'geo': {'@type': 'GeoCoordinates',
#          'latitude': '-22.5221873',
#          'longitude': '-55.7392303'},
#         'name': 'Apartamento de 52 m² com piscina em Casa Amarela, Recife - ZAP IMÓVEIS',
#         'photo': [{'@type': 'ImageObject',
#           'contentUrl': 'https://imagens.zapcorp.com.br/imoveis/2403365/gran/92f7ff6d00524e23b0f3_g.jpg'},
#          {'@type': 'ImageObject',
#           'contentUrl': 'https://imagens.zapcorp.com.br/imoveis/2403365/gran/a1ba1087e3ed4a01bfa7_g.jpg'},
#          {'@type': 'ImageObject',
#           'contentUrl': 'https://imagens.zapcorp.com.br/imoveis/2403365/gran/3bbe7b5a2d6e40c1b7c8_g.jpg'}],
#         'url': 'https://www.zapimoveis.com.br/oferta/venda+apartamento+2-quartos+casa-amarela+recife+pe+52m2+RS290000/ID-12764639/'},
#        'price': '290000',
#        'priceSpecification': {'@type': 'PriceSpecification', 'priceCurrency': 'BRL'},
#        'seller': {'@type': 'RealEstateAgent',
#         'logo': 'https://img.zapcorp.com.br/201407/28/EXT/Imoveis/2403365/img_154_2403365_LOGO.jpg',
#         'name': 'MARIA EUGENIA DE ARRUDA FALCAO',
#         'url': 'https://www.zapimoveis.com.br/imobiliaria/maria-eugenia/#{"codcliente":"2403365","transacao":"venda","subtipoimovel":"imoveis"}'}}

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
    # Extraídos do Html
    bedrooms = scrapy.Field()
    suites = scrapy.Field() # buscar tradução
    useful_area_m2 = scrapy.Field()
    total_area_m2 = scrapy.Field()
    vacancies = scrapy.Field()
