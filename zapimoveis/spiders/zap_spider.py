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
        self.file_count = 1

        sel = Selector(response=response)
        # <input type="hidden" id="quantidadeTotalPaginas" data-value="361" />
        pags = int(sel.xpath('//input[@id="quantidadeTotalPaginas"]/@data-value').extract()[0])

        self.parse_content(response)

        # for pag in range(2, pags + 1):
        for pag in range(2, 4):
            yield SplashRequest(response.url, 
                    self.parse_content,
                    endpoint='execute',
                    args={'lua_source': self.lua_script.format(pag=pag, wait=3)},
                    dont_filter=True
                    )

    def parse_content(self, response):
        filename = 'files/response{0}.html'.format(self.file_count)

        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file {0}'.format(filename))

        self.file_count += 1
