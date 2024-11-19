import sqlite3
from datetime import datetime
import json
import pickle

DB_NAME = "stock_data.db"


def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stocks (
            ticker TEXT,
            period TEXT,
            stock_data BLOB,
            predictions BLOB,
            future_predictions BLOB,
            fundamentals TEXT,
            last_updated timestamp,
            timings  TEXT,
            PRIMARY KEY (ticker,period,last_updated)
        )
    """
    )
    conn.commit()
    conn.close()


def save_data_to_db(
    ticker, period, stock_data, predictions, future_predictions, fundamentals, timings
):
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

    # serializer
    predictions_byte = pickle.dumps(predictions)
    future_predictions_byte = pickle.dumps(future_predictions)
    stock_data_byte = pickle.dumps(stock_data)
    fundamentals_byte = pickle.dumps(fundamentals)

    # Insert the record
    cursor.execute(
        """
                INSERT INTO stocks (ticker, period, stock_data,predictions,future_predictions,fundamentals,last_updated,timings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
        (
            ticker,
            period,
            stock_data_byte,
            predictions_byte,
            future_predictions_byte,
            fundamentals_byte,
            datetime.now(),
            json.dumps(timings),
        ),
    )
    conn.commit()
    conn.close()


def fetch_data_from_db(ticker, period):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    sql = """
        SELECT stock_data,predictions,future_predictions,fundamentals FROM stocks WHERE ticker ='{ticker}' AND period ='{period}' AND strftime('%Y-%m-%d', last_updated) = '{date}'
        order by last_updated DESC limit 1
    """.format(
        ticker=ticker, period=period, date=datetime.now().strftime("%Y-%m-%d")
    )
    print(sql)
    cursor.execute(sql)
    row = cursor.fetchone()
    if row:
        stock_data_pickled = row[0]
        predictions_pickled = row[1]
        future_predictions_pickled = row[2]
        fundamentals_json = row[3]
        # Deserialise the stock_data
        stock_data = pickle.loads(stock_data_pickled)
        predictions = pickle.loads(predictions_pickled)
        future_predictions = pickle.loads(future_predictions_pickled)
        fundamentals = pickle.loads(fundamentals_json)
        print("Data successfully retrieved from the database!")
        return stock_data, fundamentals, predictions, future_predictions
    else:
        print(
            "No data found in the database. Please check the ticker or Generate data."
        )
        conn.close()
        return None, None, None, None
