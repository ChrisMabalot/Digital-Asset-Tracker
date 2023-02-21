from sqlalchemy import create_engine, Column, Date, DateTime, Float, ForeignKey, Integer, String, Numeric, inspect, text
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import database_exists, create_database
from local_settings import postgresql as settings

import pandas as pd
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

def get_session(engine):
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
    session = get_session(engine)

    inspector = inspect(engine)
    if not inspector.has_table(Nft.__tablename__) or not inspector.has_table(SoldNft.__tablename__):
        Base.metadata.create_all(engine)

    # add_nft(session, 'TEST1', 'ASSET_TEST1', 150, '2023-01-05')
    # add_nft(session, 'TEST2', 'ASSET_TEST2', 250, '2023-02-2')
    # add_nft(session, 'TEST3', 'ASSET_TEST3', 50, '2023-02-20')
    # add_nft(session, 'TEST4', 'ASSET_TEST4', 50.5, '2023-02-23')
    
    # sell_nft(session, 1, 300, '2023-02-21')
    # sell_nft(session, 3, 25, '2023-02-23')

    conn = engine.connect()

    nfts_result = conn.execute(text('SELECT * FROM nfts;')).fetchall()
    sold_nfts_result = conn.execute(text('SELECT * FROM sold_nfts;')).fetchall()

    nfts_df = pd.DataFrame(nfts_result, columns=['id', 'project', 'asset', 'purchase_price', 'purchase_date'])
    sold_nfts_df = pd.DataFrame(sold_nfts_result, columns=['id', 'project', 'asset', 'purchase_price', 'sale_price', 'sale_date', 'net_return'])
    
    print(nfts_df.head())
    print(sold_nfts_df.head())

    conn.close

    test_starting_balance = 1000
    total_spent = nfts_df['purchase_price'].sum() + sold_nfts_df['purchase_price'].sum()
    total_received = sold_nfts_df['sale_price'].sum()
    net_returns = sold_nfts_df['net_return'].sum()

    print(f'Total Spent: {total_spent}')
    print(f'Net Return: {net_returns}') 
    print(f'Current P/L: {total_received - total_spent}')
    print(f'Current Balance: {test_starting_balance - total_spent + total_received}')

if __name__ == '__main__':
    main()