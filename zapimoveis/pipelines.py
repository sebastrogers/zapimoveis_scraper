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
        self.updated_count = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('SQLALCHEMY_CONFIG'))

    def close_spider(self, spider):
        spider.log("**** Total: {0} updates.".
                format(self.updated_count))
        self.engine.dispose()

    def process_item(self, item, spider):
        realty = Realty.from_item(item)
        session = Session(bind=self.engine)
        try:
            session.merge(realty)
            spider.log("**** Insert/update: {0}...".format(realty))
            session.commit()
            self.updated_count += 1
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return item
