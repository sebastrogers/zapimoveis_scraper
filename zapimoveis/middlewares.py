# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from sqlalchemy import engine_from_config
from sqlalchemy.orm import Session
from zapimoveis.models import Base, Realty
from datetime import datetime
from scrapy.http.request import Request
import re


class SqlAlchemyMiddleware(object):

    def __init__(self, config):
        self.engine = engine_from_config(config, prefix='')
        Base.metadata.create_all(self.engine)

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(crawler.settings.get('SQLALCHEMY_CONFIG'))
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # TODO [romeira]: add logs {22/03/17 23:36}
        # TODO [romeira]: refactor code {22/03/17 23:35}
        requests = dict()
        for res in result:
            if type(res) == Request:
                res_id = self.extract_url_from_id(res.url)
                if res_id:
                    requests[int(res_id)] = res
                    continue
            yield res

        if not requests:
            return
        
        res = None
        session = Session(bind=self.engine)
        try:
            # TODO [romeira]: filter by update_time:
            # .filter(Realty.update_time > today - spider.expiration_time
            # {22/03/17 23:33}
            q = session.query(Realty.id).filter(Realty.id.in_(requests.keys()))
            res = q.all()
        except:
            yield from requests.values()
            raise
        finally:
            session.close()

        filtered_count = len(res)
        spider.log('**** Foram filtradas {0} páginas recentes.'.
                format(filtered_count))
        spider.total_details -= filtered_count

        for k in requests.keys() - {id for id, in res}:
            yield requests[k]

    def extract_url_from_id(self, url):
        m = re.search('(?i)/id-(\d+)([/?#]|\s*$)', url)
        return m.group(1) if m else None

    def spider_closed(self, spider):
        self.engine.dispose()


class ZapimoveisSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
