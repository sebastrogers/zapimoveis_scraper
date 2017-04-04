# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy import engine_from_config
from sqlalchemy.orm import Session
from zapimoveis.models import Realty
from w3lib.url import urldefrag
import json
import re


class ZapimoveisPipeline(object):
    def process_item(self, item, spider):
        item['id'] = re.search('\d+', item['id']).group()

        item['price'] = item['price'].replace(',','.')

        if item['useful_area_m2']:
            item['useful_area_m2'] = item['useful_area_m2'].replace('.', '')
        if item['total_area_m2']:
            item['total_area_m2'] = item['total_area_m2'].replace('.', '')
        if item['condominium_fee']:
            item['condominium_fee'] = item['condominium_fee'].replace('.','')
        if item['iptu']:
            item['iptu'] = item['iptu'].replace('.','')

        item['seller_url'], frag = urldefrag(item['seller_url'])
        if frag:
            jsfrag = json.loads(frag)
            item['client_code'] = jsfrag.setdefault('codcliente')
            item['transaction'] = jsfrag.setdefault('transacao')
            item['property_subtype'] = jsfrag.setdefault('subtipoimovel')

        return item


class SqlAlchemyPipeline(object):
    def __init__(self, config):
        self.engine = engine_from_config(config, prefix='')
        self.update_count = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('SQLALCHEMY_CONFIG'))

    def close_spider(self, spider):
        spider.log('**** Total: {0} updates.'.
                format(self.update_count))
        self.engine.dispose()

    def process_item(self, item, spider):
        realty = Realty.from_item(item)
        session = Session(bind=self.engine)
        try:
            session.merge(realty)
            session.commit()
        except:
            session.rollback()
            raise
        else:
            self.update_count += 1
            spider.log('**** Insert/update({0}): {1}...'.
                       format(self.update_count, realty))
        finally:
            session.close()
        return item

