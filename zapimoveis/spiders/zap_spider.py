import scrapy
import json
import os
import re
from scrapy import Request
from scrapy import Selector
from scrapy_splash import SplashRequest
from zapimoveis.items import ZapItem
from w3lib.url import urljoin, url_query_cleaner


class ZapSpider(scrapy.Spider):

    name = "zap"
    allowed_domains = ['www.zapimoveis.com.br']

    # TODO [romeira]: change listing_pages to start and end pages {23/03/17 04:43}
    # TODO [romeira]: argument: expiration time {23/03/17 04:43}
    def __init__(self, place=None, listing_pages=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listing_pages = None if not listing_pages else int(listing_pages)
        # TODO [romeira]: change to crawl/scrap {23/03/17 04:46}
        # TODO [romeira]: use object to encapsulate {23/03/17 04:51}
        self.details_count = 0
        self.listing_count = 0
        self.total_details = 0
        self.total_listings = 0

        self.start_urls = [
            self.urlfmt(urljoin('https://www.zapimoveis.com.br/venda/imoveis/',
                place or 'pe+recife')),
        ]

        self.lua_script = """
            function main(splash)
              assert(splash:go(splash.args.url))
              assert(splash:runjs([[
                      p=$('[name="txtPaginacao"]');
                      p.val({pag});
                      p.blur();
              ]]))
              assert(splash:wait({wait}))
              return splash:html()
            end
        """

    def urlfmt(self, url):
        return url_query_cleaner(url)

    def parse(self, response):
        pattern = '//input[@id="quantidadeTotalPaginas"]/@data-value'
        total_pages = int(response.xpath(pattern).
                                   extract_first().replace('.', ''))

        if self.listing_pages:
            pages = min(self.listing_pages, total_pages)
        else:
            pages = total_pages

        self.total_listings += pages

        self.log('Crawling {0} of {1} listing pages...'.
                format(pages, total_pages))

        yield from self.parse_listing(response)

        for pag in range(2, pages + 1):
            yield SplashRequest(self.urlfmt(response.url), 
                    self.parse_listing,
                    endpoint='execute',
                    args={'lua_source': self.lua_script.
                                        format(pag=pag, wait=10)},
                    dont_filter=True
                )


    def parse_listing(self, response):
        links = response.xpath('//a[@class="detalhes"]/@href').extract()
        self.total_details += len(links)

        self.listing_count += 1
        self.log("**** Crawled: {0}/{1}\t {2:0.0%} ***".
                format(self.listing_count, self.total_listings,
                       self.listing_count/self.total_listings))

        for link in links:
            yield Request(self.urlfmt(link), self.parse_detail)


    def parse_detail(self, response):
        item = ZapItem()
        self.parse_json_detail(response, item)
        self.parse_html_detail(response, item)

        # A conta aqui pode não ser exata, pois links repetidos são filtrados
        self.details_count += 1
        self.log("**** Scraped: {0}/{1}\t {2:0.0%} ***".
                format(self.details_count, self.total_details,
                       self.details_count/self.total_details))

        return item


    def parse_html_detail(self, response, item):
        lis = response.css('div.informacoes-imovel ul > li')

        item['bedrooms'] = lis.re_first('(?i)<li>\s*(\d+).*quarto')
        item['suites'] = lis.re_first('(?i)<li>\s*(\d+).*su[ií]te') # buscar tradução
        item['useful_area_m2'] = lis.re_first('(?i)<li>\s*(\d+(\.\d+)?).*[aá]rea\s+[úu]til')
        item['total_area_m2'] = lis.re_first('(?i)<li>\s*(\d+(\.\d+)?).*[aá]rea\s+total')
        item['vacancies'] = lis.re_first('(?i)<li>\s*(\d+).*vaga')

    def parse_json_detail(self, response, item):
        pattern = '/html/body/script[@type="application/ld+json"]/text()'
        jsitem = json.loads(response.xpath(pattern).extract_first())[1]

        item['action'] = jsitem.setdefault('@type')
        item['price'] = jsitem.setdefault('price')
        if 'priceSpecification' in jsitem:
            item['currency'] = jsitem['priceSpecification'].\
                    setdefault('priceCurrency')

        if 'object' in jsitem:
            jsobject = jsitem['object']
            item['type'] = jsobject.setdefault('@type')
            item['description'] = jsobject.setdefault('description')
            item['name'] = jsobject.setdefault('name')
            item['url'] = jsobject.setdefault('url')
            item['id'] = jsobject.setdefault('@id')

            if 'address' in jsobject:
                jsaddress = jsobject['address']
                if 'addressCountry' in jsaddress:
                    item['country'] = jsaddress['addressCountry'].\
                            setdefault('name')
                item['city'] = jsaddress.setdefault('addressLocality')
                item['state'] = jsaddress.setdefault('addressRegion')
                item['postal_code'] = jsaddress.setdefault('postalCode')
                item['street'] = jsaddress.setdefault('streetAddress')

            if 'geo' in jsobject:
                item['latitude'] = jsobject['geo'].setdefault('latitude')
                item['longitude'] = jsobject['geo'].setdefault('longitude')

        if 'seller' in jsitem:
            jsseller = jsitem['seller']
            item['seller_type'] = jsseller.setdefault('@type')
            item['seller_name'] = jsseller.setdefault('name')
            item['seller_url'] = jsseller.setdefault('url')
