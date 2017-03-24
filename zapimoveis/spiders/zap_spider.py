import scrapy
import json
import re
from scrapy import Request
from scrapy_splash import SplashRequest
from zapimoveis.items import ZapItem
from w3lib.url import urljoin, url_query_cleaner
from datetime import timedelta


class ZapSpider(scrapy.Spider):

    name = 'zap'
    allowed_domains = ['www.zapimoveis.com.br']

    def __init__(self, place=None, start=1, 
                 count=None, expiry=None, *args, **kwargs):
        super(ZapSpider, self).__init__(*args, **kwargs)
        self.start = int(start) if start else 1
        self.count = int(count) if count else None
        self.expiry = self.parse_timedelta(expiry)

        self.crawl_count = 0
        self.scrape_count = 0
        self.total_crawl = 0
        self.total_scrape = 0

        self.start_urls = [
            self.urlfmt(urljoin('https://www.zapimoveis.com.br/venda/imoveis/',
                place or 'pe+recife' if place != 'all' else '')),
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


    def parse(self, response):
        pattern = '//input[@id="quantidadeTotalPaginas"]/@data-value'
        total_pages = int(response.xpath(pattern).
                                   extract_first().replace('.', ''))
        from_page = self.start
        if self.count:
            to_page = min(self.start + self.count - 1, total_pages)
        else:
            to_page = total_pages

        pages_count = (to_page - from_page + 1)
        self.total_crawl += pages_count

        self.log('Crawling {0} of {1} listing pages...'.
                format(pages_count, total_pages))

        if from_page == 1:
            yield from self.parse_listing(response)
            from_page += 1

        for pag in range(from_page, to_page + 1):
            yield SplashRequest(self.urlfmt(response.url), 
                    self.parse_listing,
                    endpoint='execute',
                    args={'lua_source': self.lua_script.
                                        format(pag=pag, wait=7)},
                    dont_filter=True
                )


    def parse_listing(self, response):
        links = response.xpath('//a[@class="detalhes"]/@href').extract()
        self.total_scrape += len(links)

        self.crawl_count += 1
        self.log('**** Crawled: {0}/{1}\t {2:0.0%}'.
                format(self.crawl_count, self.total_crawl,
                       self.crawl_count/self.total_crawl))

        for link in links:
            yield Request(self.urlfmt(link), self.parse_detail)


    def parse_detail(self, response):
        item = ZapItem()
        self.parse_json_detail(response, item)
        self.parse_html_detail(response, item)

        # A conta aqui pode não ser exata, pois links repetidos são filtrados
        self.scrape_count += 1
        self.log('**** Scraped: {0}/{1}\t {2:0.0%}'.
                format(self.scrape_count, self.total_scrape,
                       self.scrape_count/self.total_scrape))

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


    # TODO [romeira]: put those methods in a new module {23/03/17 23:55}
    # Formato: 1w1d1h1m
    def parse_timedelta(self, str_time):
        if not str_time:
            return None
        pattern = ('(?i)' + '((?P<{}>(\d*\.)?\d+){})?' * 4).\
                format('weeks', 'w', 'days', 'd', 'hours', 'h', 'minutes', 'm')
        m = re.match(pattern, str_time)

        return timedelta(**{k:float(v) for k,v in m.groupdict().items() if v})\
               if m.string else None
        
    def urlfmt(self, url):
        return url_query_cleaner(url)

