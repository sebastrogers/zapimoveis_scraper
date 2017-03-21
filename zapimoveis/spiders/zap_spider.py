import scrapy
from scrapy import Selector
from scrapy_splash import SplashRequest


class ZapSpider(scrapy.Spider):
    name = "zap"

    def __init__(self):
        self.lua_script = """
            function main(splash)
              assert(splash:go(splash.args.url))
              assert(splash:runjs("p=$('[name=\\"txtPaginacao\\"]');p.val({pag});p.blur();"))
              assert(splash:wait({wait}))
              return splash:html()
            end
        """

    def start_requests(self):
        urls = [
                'https://www.zapimoveis.com.br/venda/imoveis/pe+recife/',
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        sel = Selector(response=response)
        # <input type="hidden" id="quantidadeTotalPaginas" data-value="361" />
        pags = int(sel.xpath('//input[@id="quantidadeTotalPaginas"]/@data-value').extract()[0])

        self.splash_count = 1
        filename = 'files/response.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)


        # for pag in range(2, pags + 1):
        for pag in range(2, 6):
            yield SplashRequest(response.url, 
                    self.parse_splash,
                    endpoint='execute',
                    args={'lua_source': self.lua_script.format(pag=pag, wait=2) },
                    dont_filter=True
                    )

    def parse_splash(self, response):
        filename = 'files/response_splash{0}.html'.format(self.splash_count)
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        self.splash_count += 1
