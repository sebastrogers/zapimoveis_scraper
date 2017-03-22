import scrapy
import json
import os
import re
from scrapy import Request
from scrapy import Selector
from scrapy_splash import SplashRequest
from zapimoveis.items import ZapItem


class ZapSpider(scrapy.Spider):

    name = "zap"
    allowed_domains = ['www.zapimoveis.com.br']

    def __init__(self, place=None, listing_pages=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listing_pages = None if not listing_pages else int(listing_pages)
        self.details_count = 0
        self.listing_count = 0
        self.total_details = 0
        self.total_listings = 0

        if not os.path.exists('files/'):
            os.mkdir('files')

        self.start_urls = [
            'https://www.zapimoveis.com.br/venda/imoveis/{0}'.format(
                    place or 'pe+recife'),
        ]

        self.lua_script = """
            function main(splash)
              assert(splash:go(splash.args.url))
              assert(splash:runjs("p=$('[name=\\"txtPaginacao\\"]');p.val({pag});p.blur();"))
              assert(splash:wait({wait}))
              return splash:html()
            end
        """


    def parse(self, response):
        pattern = '//input[@id="quantidadeTotalPaginas"]/@data-value'
        total_pages = int(response.xpath(pattern).extract_first())

        if self.listing_pages:
            pages = min(self.listing_pages, total_pages)
        else:
            pages = total_pages

        self.total_listings += pages

        self.log('Crawling {0} of {1} listing pages...'.
                format(pages, total_pages))

        yield from self.parse_listing(response)

        for pag in range(2, pages + 1):
            yield SplashRequest(response.url, 
                    self.parse_listing,
                    endpoint='execute',
                    args={'lua_source': self.lua_script.
                                        format(pag=pag, wait=5)},
                    dont_filter=True
                    )


    def parse_listing(self, response):
        links = response.xpath('//a[@class="detalhes"]/@href').extract()
        self.total_details += len(links)

        with open('files/links.txt', 'a') as f:
            f.write('\n'.join(links))
        with open('files/listing_{0:03d}.html'.
                format(self.listing_count), 'wb') as f:
            f.write(response.body)

        for link in links:
            # O split remove a querystring
            yield Request(link.split('?',1)[0], self.parse_detail)

        self.listing_count += 1
        self.log("**** Listings: {0}/{1}\t {2:0.0%} ***".
                format(self.listing_count, self.total_listings,
                       self.listing_count/self.total_listings))


    def parse_detail(self, response):
        with open('files/details_{0:04d}.html'.
                format(self.details_count), 'wb') as f:
            f.write(response.body)

        item = ZapItem()
        self.parse_json_detail(response, item)
        self.parse_html_detail(response, item)

        # A conta aqui pode não bater, pois links repetidos são filtrados
        self.details_count += 1
        self.log("**** Scraped: {0}/{1}\t {2:0.0%} ***".
                format(self.details_count, self.total_details,
                       self.details_count/self.total_details))

        return item


    def parse_html_detail(self, response, item):
        lis = response.css('div.informacoes-imovel ul > li')

        item['bedrooms'] = lis.re_first('(?i)<li>\s*(\d+).*quarto')
        item['suites'] = lis.re_first('(?i)<li>\s*(\d+).*su[ií]te') # buscar tradução
        item['useful_area_m2'] = lis.re_first('(?i)<li>\s*(\d+).*[aá]rea\s+[úu]til')
        item['total_area_m2'] = lis.re_first('(?i)<li>\s*(\d+).*[aá]rea\s+total')
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
            if '@id' in jsobject:
                item['id'] = re.search('\d+', jsobject['@id']).group()
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
            if 'url' in jsseller:
                url, *c_params = jsseller['url'].split('#',1)
                item['seller_url'] = url
                c_params = c_params[0]
                if c_params:
                    c_params = json.loads(c_params)
                    item['client_code'] = c_params.setdefault('codcliente')
                    item['transaction'] = c_params.setdefault('transacao')
                    item['property_subtype'] = c_params.setdefault('subtipoimovel')

