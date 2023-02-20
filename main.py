from sqlalchemy import create_engine, Column, Date, DateTime, Float, ForeignKey, Integer, String, Numeric, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from local_settings import postgresql as settings

import plotly.express as ps

Base = declarative_base()

class Nft(Base):
    __tablename__ = 'nfts'

    id = Column(Integer, primary_key=True)
    project = Column(String(255), nullable=False)
    asset = Column(String(255), nullable=False)
    purchase_price = Column(Numeric(10,2))
    purchase_date = Column(Date)

class SoldNft(Base):
    __tablename__ = 'sold_nfts'

    id = Column(Integer, primary_key=True)
    project = Column(String(255), nullable=False)
    asset = Column(String(255), nullable=False)
    purchase_price = Column(Numeric(10,2))
    sale_price = Column(Numeric(10,2))
    sale_date = Column(Date)
    net_return = Column(Numeric(10,2))

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

def add_nft(session, project, asset, purchase_price, purchase_date):
    nft = Nft(project = project, asset = asset, purchase_price = purchase_price, purchase_date = purchase_date)
    session.add(nft)
    session.commit()
    return nft.id

def sell_nft(session, nft_id, sale_price, sale_date):
    nft = session.query(Nft).filter(Nft.id == nft_id).first()
    if not nft:
        raise ValueError(f'NFT with id {nft_id} not found.')
    
    sold_nft = SoldNft(id = nft_id, project = nft.project, asset = nft.asset, purchase_price = nft.purchase_price, sale_price = sale_price, sale_date = sale_date, net_return = (sale_price-nft.purchase_price))
    session.add(sold_nft)
    session.delete(nft)
    session.commit()
    return sold_nft.id 

def main():
    engine = get_engine_from_settings()
    session = get_session()

    inspector = inspect(engine)
    if not inspector.has_table(Nft.__tablename__) or not inspector.has_table(SoldNft.__tablename__):
        Base.metadata.create_all(engine)

    # add_nft(session, 'TEST2', 'ASSET_TEST2', 150, '2023-02-23')
    # sell_nft(session, 1, 150, '2023-02-20')

    nfts = session.query(Nft).all()
    sold_nfts = session.query(SoldNft).all()

    if len(nfts):
        print("Held NFT's:")
        for nft in nfts:
            print(nft.purchase_date, nft.project, nft.asset, nft.purchase_price)
            print('')
    else:
        print("No NFT's currently held.")
        print('')
    
    if len(sold_nfts):
        print("Sold NFT's")
        for nft in sold_nfts:
            print(nft.sale_date, nft.project, nft.asset, nft.purchase_price, nft.sale_price, nft.net_return)
    else:
        print("No NFT's have been sold.")

if __name__ == '__main__':
    main()