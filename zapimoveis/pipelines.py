# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from zapimoveis.models import Base, Realty

Session = sessionmaker()

class ZapimoveisPipeline(object):
    def process_item(self, item, spider):
        return item

class SqlAlchemyPipeline(object):
    def __init__(self, config):
        self.engine = engine_from_config(config, prefix='')
        Base.metadata.create_all(self.engine)
        Session.configure(bind=self.engine)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('SQLALCHEMY_CONFIG'))

    # def open_spider(self, spider):
    #     self.session = Session(bind=self.engine)

    def close_spider(self, spider):
        self.engine.dispose()

    def process_item(self, item, spider):
        session = Session()
        try:
            session.merge(Realty.from_item(item))
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return item
