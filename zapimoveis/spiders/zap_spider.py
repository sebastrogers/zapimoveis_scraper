import scrapy


class ZapSpider(scrapy.Spider):
    name = "zap"

    def start_requests(self):
        urls = [
                # 'https://www.zapimoveis.com.br/venda/imoveis/pe+recife/#{"precomaximo":"2147483647","parametrosautosuggest":[{"Bairro":"","Zona":"","Cidade":"RECIFE","Agrupamento":"","Estado":"PE"}],"pagina":"1","ordem":"Relevancia","paginaOrigem":"ResultadoBusca","semente":"469630922","formato":"Lista"}',
                'https://www.zapimoveis.com.br/venda/imoveis/pe+recife/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # page = response.url.split("/")[-2]
        filename = 'test.html' # 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
