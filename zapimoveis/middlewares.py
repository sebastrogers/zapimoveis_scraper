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
from w3lib.url import urlsplit


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

        # TODO [romeira]: refactor code {22/03/17 23:35}
        requests = dict()
        for res in result:
            if isinstance(res, Request):
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
            q = session.query(Realty.id).filter(Realty.id.in_(requests.keys()))
            if spider.expiry:
                q = q.filter(Realty.update_time > (datetime.now() - spider.expiry))

            res = q.all()
        except:
            yield from requests.values()
            raise
        finally:
            session.close()

        filtered_count = len(res)
        spider.log('**** Filtered: {0} (recently scraped).'.
                format(filtered_count))
        spider.total_scrape -= filtered_count

        for k in requests.keys() - {id for id, in res}:
            yield requests[k]

    def extract_url_from_id(self, url):
        m = re.search('(?i)/id-(\d+)', urlsplit(url).path)
        return m.group(1) if m else None

    def spider_closed(self, spider):
        self.engine.dispose()

