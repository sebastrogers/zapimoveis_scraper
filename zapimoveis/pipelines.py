# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy import engine_from_config
from sqlalchemy.orm import Session
from zapimoveis.models import Base, Realty


class ZapimoveisPipeline(object):
    def process_item(self, item, spider):
        return item

class SqlAlchemyPipeline(object):
    def __init__(self, config):
        self.engine = engine_from_config(config, prefix='')
        Base.metadata.create_all(self.engine)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('SQLALCHEMY_CONFIG'))

    def open_spider(self, spider):
        self.session = Session(bind=self.engine)

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        try:
            # TODO [romeira]: verificar se o item já existe. se sim,
            # atualizar {22/03/17 09:31}
            self.session.add(Realty.from_item(item))
            self.session.commit()
        except:
            self.session.rollback()
            raise
        return item
