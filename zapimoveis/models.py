from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

Base = declarative_base()


class Realty(Base):
    __tablename__ = 'realties'

    # TODO [romeira]: apply type constraints {23/03/17 05:58}
    id = Column(Integer, primary_key=True)
    name = Column(String)
    action = Column(String)
    type = Column(String)
    country = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    street = Column(String)
    district = Column(String)
    description = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    url = Column(String)
    price = Column(Float)
    currency = Column(String)
    seller_type = Column(String)
    seller_name = Column(String)
    seller_url = Column(String)
    client_code = Column(Integer)
    transaction = Column(String)
    property_subtype = Column(String)
    bedrooms = Column(Integer)
    suites = Column(Integer) # buscar tradução
    useful_area_m2 = Column(Integer)
    total_area_m2 = Column(Integer)
    vacancies = Column(Integer)
    condominium_fee = Column(Float)
    iptu = Column(Float)
    update_time = Column(DateTime)

    @classmethod
    def from_item(cls, item):
        realty = cls(**dict(item))
        realty.update_time = datetime.now()
        return realty

    def __repr__(self):
        return '<Realty(id={0}, name="{1}")>'.format(self.id, self.name)
