import sqlite3
from datetime import datetime
import json
import pickle
DB_NAME = "stock_data.db"

def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            ticker TEXT,
            period TEXT,
            stock_data BLOB,
            fundamentals TEXT,
            last_updated timestamp,
            PRIMARY KEY (ticker,period,last_updated)
        )
    ''')
    conn.commit()
    conn.close()

def save_data_to_db(ticker, period, stock_data, fundamentals):
    """
    Saves stock data and fundamentals to the database.

    Parameters:
    - ticker (str): The stock ticker.
    - period (str): The time period.
    - stock_data (pd.DataFrame): The stock data.
    - fundamentals (dict): The stock fundamentals.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Insert the record
    cursor.execute('''
                INSERT INTO stocks (ticker, period, stock_data,fundamentals,last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (ticker,period,pickle.dumps(stock_data),json.dumps(fundamentals),datetime.now())
                   )
    conn.commit()
    conn.close()


def fetch_data_from_db(ticker, period):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    sql='''
        SELECT stock_data,fundamentals FROM stocks WHERE ticker ='{ticker}' AND period ='{period}' AND strftime('%Y-%m-%d', last_updated) = '{date}'
        order by last_updated DESC limit 1
    '''.format(ticker=ticker, period=period, date=datetime.now().strftime('%Y-%m-%d'))
    print(sql)
    cursor.execute(sql)
    row = cursor.fetchone()
    if row:
        stock_data_pickled = row[0]
        fundamentals_json = row[1]
        # Unpickle the stock_data
        stock_data = pickle.loads(stock_data_pickled)
        fundamentals = json.loads(fundamentals_json)
        print('Data successfully retrieved from the database!')
        return stock_data, fundamentals
    else:
        print('No data found in the database. Please check the ticker or Generate data.')
        conn.close()
        return None,None


