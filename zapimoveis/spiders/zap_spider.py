import scrapy
import json
from scrapy import Selector
from scrapy_splash import SplashRequest
from zapimoveis.items import ZapItem


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
        pattern = '//input[@id="quantidadeTotalPaginas"]/@data-value'
        total_pages = int(response.xpath(pattern).extract()[0])

        if self.max_pages:
            pages = min(self.max_pages, total_pages)
        else:
            pages = total_pages

        self.logger.info('Crawling {0} of {1} pages...'.
                format(pages, total_pages))

        yield from self.parse_content(response)

        for pag in range(2, pages + 1):
            yield SplashRequest(response.url, 
                    self.parse_content,
                    endpoint='execute',
                    args={'lua_source': self.lua_script.format(pag=pag, wait=3)},
                    dont_filter=True
                    )

    def parse_content(self, response):
        pattern = '/html/body/script[@type="application/ld+json"]/text()'
        js = json.loads(response.xpath(pattern).extract()[0])

        for jsitem in js[2:]:
            item = ZapItem()
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

            yield item
