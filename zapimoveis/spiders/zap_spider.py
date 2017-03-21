import scrapy
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
        self.splash_count = 1
        filename = 'response.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        yield SplashRequest(response.url, 
                self.parse_splash,
                endpoint='execute',
                args={'lua_source': self.lua_script.format(pag=20, wait=2) },
                dont_filter=True
                )

    def parse_splash(self, response):
        filename = 'response_splash{0}.html'.format(self.splash_count)
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        self.splash_count += 1
