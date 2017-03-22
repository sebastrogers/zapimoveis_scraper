import scrapy
import json
from scrapy import Request
from scrapy import Selector
from scrapy_splash import SplashRequest
from zapimoveis.items import ZapItem
import os


class ZapSpider(scrapy.Spider):

    name = "zap"
    allowed_domains = ['www.zapimoveis.com.br']

    def __init__(self, place=None, max_pages=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = None if not max_pages else int(max_pages)
        self.start_urls = [
            'https://www.zapimoveis.com.br/venda/imoveis/{0}'.format(
                'pe+recife' if not place else place),
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
        self.file_count = 1
        if not os.path.exists('files/'):
            os.mkdir('files')

        pattern = '//input[@id="quantidadeTotalPaginas"]/@data-value'
        total_pages = int(response.xpath(pattern).extract_first())

        if self.max_pages:
            pages = min(self.max_pages, total_pages)
        else:
            pages = total_pages

        self.logger.info('Crawling {0} of {1} pages...'.
                format(pages, total_pages))

        yield from self.parse_listing(response)

        for pag in range(2, pages + 1):
            yield SplashRequest(response.url, 
                    self.parse_listing,
                    endpoint='execute',
                    args={'lua_source': self.lua_script.format(pag=pag, wait=5)},
                    dont_filter=True
                    )


    def parse_listing(self, response):
        links = response.xpath('//a[@class="detalhes"]/@href').extract()

        with open('files/links.txt', 'a') as f:
            f.write('\n'.join(links))

        for link in links:
            yield Request(link, self.parse_detail)


    def parse_detail(self, response):
        with open('files/response_{0:03d}.html'.format(self.file_count), 'wb') as f:
            f.write(response.body)
            self.file_count += 1

        item = ZapItem()
        self.parse_json_detail(response, item)
        self.parse_html_detail(response, item)

        return item


    def parse_html_detail(self, response, item):
        lis = response.css('div.informacoes-imovel li')

        item['bedrooms'] = lis.re_first('(?i)<li>\s*(\d+).*quarto')
        item['suites'] = lis.re_first('(?i)<li>\s*(\d+).*su[ií]te') # buscar tradução
        item['useful_area_m2'] = lis.re_first('(?i)<li>\s*(\d+\.?\d*).*[aá]rea\s+[úu]til')
        item['total_area_m2'] = lis.re_first('(?i)<li>\s*(\d+\.?\d*).*[aá]rea\s+total')
        item['vacancies'] = lis.re_first('(?i)<li>\s*(\d+).*vaga')

    def parse_json_detail(self, response, item):
        pattern = '/html/body/script[@type="application/ld+json"]/text()'
        jsitem = json.loads(response.xpath(pattern).extract_first())[1]

        item['action'] = jsitem['@type']
        item['price'] = jsitem['price']
        item['currency'] = jsitem['priceSpecification']['priceCurrency']

        jsobject = jsitem['object']
        item['id'] = jsobject['@id']
        item['type'] = jsobject['@type']

        jsaddress = jsobject['address']
        item['country'] = jsaddress['addressCountry']['name']
        item['city'] = jsaddress['addressLocality']
        item['state'] = jsaddress['addressRegion']
        item['postal_code'] = jsaddress['postalCode']
        item['street'] = jsaddress['streetAddress']

        item['description'] = jsobject['description']
        item['latitude'] = jsobject['geo']['latitude']
        item['longitude'] = jsobject['geo']['longitude']
        item['name'] = jsobject['name']
        item['url'] = jsobject['url']


        jsseller = jsitem['seller']
        item['seller_type'] = jsseller['@type']
        item['seller_name'] = jsseller['name']
        item['seller_url'] = jsseller['url']
