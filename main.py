from sqlalchemy import create_engine, Column, Date, DateTime, Float, ForeignKey, Integer, String, Numeric, inspect, text
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import database_exists, create_database
from local_settings import postgresql as settings

import pandas as pd
import plotly.express as ps

Base = declarative_base()

class Asset(Base):
    __tablename__ = 'assets'

    id = Column(Integer, primary_key=True)
    project = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)

class Transaction(Base):
    __tablename__ = 'transactions'

    transaction_id = Column(Integer, primary_key=True, nullable=False)
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False)
    price = Column(Numeric(10,2), nullable=False)
    date = Column(Date, nullable=False)
    type = Column(String(255), nullable=False)

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

def add_asset(session, project, name):
    asset = Asset(project = project, name = name)
    session.add(asset)
    session.commit()
    print(f'Asset successfully added with ID {asset.id}')
    return asset.id

def add_transaction(session, asset_id, price, date, type):
    asset = session.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise ValueError(f'Asset not found with ID {id}.')
    
    transaction = Transaction(asset_id = asset_id, price = price, date = date, type = type)
    session.add(transaction)
    session.commit()
    print(f'{type} transaction successfully added for asset with ID {asset_id}')
    return transaction.asset_id

def main():
    engine = get_engine_from_settings()
    session = get_session(engine)

    inspector = inspect(engine)
    if not inspector.has_table(Asset.__tablename__) or not inspector.has_table(Transaction.__tablename__):
        Base.metadata.create_all(engine)

    # add_asset(session, 'Project1', 'Asset1')
    # add_asset(session, 'Project1', 'Asset2')
    # add_asset(session, 'Project2', 'Asset1')
    # add_asset(session, 'Project3', 'Asset1')
    
    # add_transaction(session, 1, 100, '2023-1-20', 'Buy')
    # add_transaction(session, 1, 300, '2023-1-25', 'Sell')
    # add_transaction(session, 2, 150, '2023-1-26', 'Buy')
    # add_transaction(session, 3, 50, '2023-1-26', 'Buy')
    # add_transaction(session, 4, 10.5, '2023-1-26', 'Buy')
    # add_transaction(session, 4, 173, '2023-2-10', 'Sell')


    # conn = engine.connect()

    # nfts_result = conn.execute(text('SELECT * FROM nfts;')).fetchall()
    # sold_nfts_result = conn.execute(text('SELECT * FROM sold_nfts;')).fetchall()

    # nfts_df = pd.DataFrame(nfts_result, columns=['id', 'project', 'asset', 'purchase_price', 'purchase_date'])
    # sold_nfts_df = pd.DataFrame(sold_nfts_result, columns=['id', 'project', 'asset', 'purchase_date','purchase_price', 'sale_price', 'sale_date', 'net_return'])
    
    # print(nfts_df.head())
    # print(sold_nfts_df.head())

    # conn.close

    conn = engine.connect()

    transactions_query = conn.execute(text('SELECT price, date, type FROM transactions ORDER BY date ASC')).fetchall()
    transactions_df = pd.DataFrame(transactions_query, columns=['price', 'date', 'type'])
    print(transactions_df.head(10))

    balance = 1000 # Initialisation of the starting balance.

    updated_balances = []
    for date, group in transactions_df.groupby('date'):
        for _, row in group.iterrows():
            if row['type'] == 'Buy':
                balance -= row['price']
            elif row['type'] == 'Sell':
                balance += row['price']
        updated_balances.append(balance)

    balanced_df = pd.DataFrame({'date': transactions_df['date'].unique(), 'balance': updated_balances})
    print(balanced_df)

    conn.close

    # test_starting_balance = 1000
    # total_spent = nfts_df['purchase_price'].sum() + sold_nfts_df['purchase_price'].sum()
    # total_received = sold_nfts_df['sale_price'].sum()
    # net_returns = sold_nfts_df['net_return'].sum()

    # print(f'Total Spent: {total_spent}')
    # print(f'Net Return: {net_returns}') 
    # print(f'Current P/L: {total_received - total_spent}')
    # print(f'Current Balance: {test_starting_balance - total_spent + total_received}')

    # merged_df = pd.merge(nfts_df, sold_nfts_df, how='outer', on=['id', 'project', 'asset', 'purchase_price', 'purchase_date']).sort_values(by='id', ascending=True)
    # print(merged_df.head())



if __name__ == '__main__':
    main()