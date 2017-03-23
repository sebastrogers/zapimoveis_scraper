# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy import engine_from_config
from sqlalchemy.orm import Session
from zapimoveis.models import Realty


class ZapimoveisPipeline(object):
    def process_item(self, item, spider):
        return item

class SqlAlchemyPipeline(object):
    def __init__(self, config):
        self.engine = engine_from_config(config, prefix='')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('SQLALCHEMY_CONFIG'))

    def close_spider(self, spider):
        self.engine.dispose()

    def process_item(self, item, spider):
        session = Session(bind=self.engine)
        try:
            session.merge(Realty.from_item(item))
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return item
