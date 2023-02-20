from sqlalchemy import create_engine, Column, Date, DateTime, Float, ForeignKey, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from local_settings import postgresql as settings

Base = declarative_base()

class Nft(Base):
    __tablename__ = 'nfts'

    id = Column(Integer, primary_key=True)
    project = Column(String(255), nullable=False)
    purchase_price = Column=(Numeric(10,2))
    purchase_date = Column(Date)

class SoldNft(Base):
    __tablename__ = 'sold_nfts'

    id = Column(Integer, primary_key=True)
    nft_id = Column(Integer, ForeignKey('nfts.id'), nullable=False)
    purchase_price = Column(Numeric(10,2))
    sale_price = Column(Numeric(10,2))
    sale_date = Column(Date)
