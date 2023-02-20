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
    purchase_price = Column(Numeric(10,2))
    purchase_date = Column(Date)

class SoldNft(Base):
    __tablename__ = 'sold_nfts'

    id = Column(Integer, primary_key=True)
    nft_id = Column(Integer, ForeignKey('nfts.id'), nullable=False)
    purchase_price = Column(Numeric(10,2))
    sale_price = Column(Numeric(10,2))
    sale_date = Column(Date)

def get_engine(user, passwd, host, port, db):
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)
        print('New Database created.')
    engine = create_engine(url, pool_size=50, echo=False)
    print('Database successfully found.')
    return engine

def get_engine_from_settings():
    keys = ['pguser', 'pgpasswd', 'pghost', 'pgport', 'pgdb']
    if not all (key in keys for key in settings.keys()):
        raise Exception('Bad config')

    return get_engine(
    settings['pguser'],
    settings['pgpasswd'],
    settings['pghost'],
    settings['pgport'],
    settings['pgdb']
    )

def get_session():
    engine = get_engine_from_settings()
    session = sessionmaker(bind = engine)()
    return session

def main():
    engine = get_engine_from_settings()
    session = get_session

if __name__ == '__main__':
    main()