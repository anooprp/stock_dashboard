import yfinance as yf
import requests
from prediction.database_handler import *
from prediction.lstm import *
import time

ALPHA_VANTAGE_API_KEY = 'YOUR_API_KEY_HERE'


def compute_rsi(data, window=14):
    """
    Compute the Relative Strength Index (RSI) for a given stock data.
    """
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)

    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def fetch_yahoo_data(tickers, period='1y'):
    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period=period)
        stock_data['SMA_20'] = stock_data['Close'].rolling(window=20).mean()
        stock_data['SMA_50'] = stock_data['Close'].rolling(window=50).mean()
        # Calculate RSI and add to stock_data
        stock_data['RSI'] = compute_rsi(stock_data['Close'])
        data[ticker] = stock_data
    return data

def fetch_yahoo_fundamentals(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    fundamentals = {
        "Market Cap": info.get('marketCap', 'N/A'),
        "P/E Ratio": info.get('trailingPE', 'N/A'),
        "Beta": info.get('beta', 'N/A'),
        "Dividend Yield": info.get('dividendYield', 'N/A'),
        "EPS": info.get('epsTrailingTwelveMonths', 'N/A'),
        "Sector": info.get('sector', 'N/A'),
        "Industry": info.get('industry', 'N/A'),
        "Exchange": info.get('exchange', 'N/A'),
        "Currency": info.get('currency', 'N/A'),
        "Country": info.get('country', 'N/A'),
        "Analyst Target Price": info.get('targetMeanPrice', 'N/A'),
    }
    return fundamentals

def fetch_alpha_vantage_fundamentals(ticker):
    url = f'https://www.alphavantage.co/query'
    params = {
        'function': 'OVERVIEW',
        'symbol': ticker,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    fundamentals = {
        "Market Cap": data.get('MarketCapitalization', 'N/A'),
        "P/E Ratio": data.get('PERatioTTM', 'N/A'),
        "Beta": data.get('Beta', 'N/A'),
        "Dividend Yield": data.get('DividendYield', 'N/A'),
        "EPS": data.get('EPS', 'N/A'),
        "Sector": data.get('Sector', 'N/A'),
        "Industry": data.get('Industry', 'N/A'),
        "Exchange": data.get('Exchange', 'N/A'),
        "Currency": data.get('Currency', 'N/A'),
        "Country": data.get('Country', 'N/A'),
        "Analyst Target Price": data.get('AnalystTargetPrice', 'N/A'),
    }
    return fundamentals



def fetch_stock_data1(tickers, period='1y'):
    timings = {}  # Dictionary to store time taken for each step
    # Start total timer
    total_start_time = time.perf_counter()

    # Step 1: Fetch data from DB
    start_time = time.perf_counter()
    stock_data, fundamentals, predictions, future_predictions = fetch_data_from_db(tickers, period)
    timings['fetch_data_from_db'] = time.perf_counter() - start_time

    if fundamentals:
        return stock_data, fundamentals, predictions, future_predictions
    else:
        # Step 2: Fetch fresh data
        print("Generating Data using API's")
        start_time = time.perf_counter()
        stock_data = fetch_yahoo_data([tickers], period=period)
        timings['fetch_yahoo_data'] = time.perf_counter() - start_time

        start_time = time.perf_counter()
        fundamentals = fetch_yahoo_fundamentals(tickers)
        timings['fetch_yahoo_fundamentals'] = time.perf_counter() - start_time

        # Step 3: Fetch Alpha Vantage fundamentals if any value is 'N/A'
        start_time = time.perf_counter()
        if any(value == 'N/A' for value in fundamentals.values()):
            alpha_fundamentals = fetch_alpha_vantage_fundamentals(tickers)
            for key, value in fundamentals.items():
                if value == 'N/A':
                    fundamentals[key] = alpha_fundamentals.get(key, 'N/A')
        timings['fetch_alpha_vantage_fundamentals'] = time.perf_counter() - start_time

        # Step 4: Prepare data for LSTM model
        start_time = time.perf_counter()
        X, y, scaler = prepare_lstm_data(stock_data[tickers])
        timings['prepare_lstm_data'] = time.perf_counter() - start_time

        # Step 5: Build and train the model
        start_time = time.perf_counter()
        model = build_cnn_lstm_model((X.shape[1], 1))
        timings['build_cnn_lstm_model'] = time.perf_counter() - start_time

        start_time = time.perf_counter()
        model = train_lstm_model(model, X, y)
        timings['train_lstm_model'] = time.perf_counter() - start_time

        # Step 6: Predict stock prices
        start_time = time.perf_counter()
        predictions, future_predictions = predict_stock_prices_lstm(model, stock_data[tickers], scaler)
        timings['predict_stock_prices_lstm'] = time.perf_counter() - start_time

        # Step 7: Save data to DB
        timings['total'] = time.perf_counter() - total_start_time
        save_data_to_db(tickers, period, stock_data, predictions, future_predictions, fundamentals, timings)
        # Start total timer

        print(timings)
        return stock_data, fundamentals, predictions, future_predictions

def fetch_stock_data(tickers, period='1y'):
    timings = {}  # Dictionary to store time taken for each step
    # Start total timer
    total_start_time = time.perf_counter()

    # Step 1: Fetch data from DB
    start_time = time.perf_counter()
    stock_data, fundamentals, predictions, future_predictions = fetch_data_from_db(tickers, period)
    timings['fetch_data_from_db'] = time.perf_counter() - start_time

    if fundamentals:
        return stock_data, fundamentals, predictions, future_predictions
    else:
        # Step 2: Fetch fresh data
        print("Generating Data using API's")
        start_time = time.perf_counter()
        stock_data = fetch_yahoo_data([tickers], period=period)  # Pass tickers directly (not as a list of a list)
        timings['fetch_yahoo_data'] = time.perf_counter() - start_time

        start_time = time.perf_counter()
        fundamentals = fetch_yahoo_fundamentals(tickers)
        timings['fetch_yahoo_fundamentals'] = time.perf_counter() - start_time

        # Step 3: Fetch Alpha Vantage fundamentals if any value is 'N/A'
        start_time = time.perf_counter()
        if any(value == 'N/A' for value in fundamentals.values()):
            alpha_fundamentals = fetch_alpha_vantage_fundamentals(tickers)
            for key, value in fundamentals.items():
                if value == 'N/A':
                    fundamentals[key] = alpha_fundamentals.get(key, 'N/A')
        timings['fetch_alpha_vantage_fundamentals'] = time.perf_counter() - start_time

        # Step 4: Prepare data for LSTM model
        start_time = time.perf_counter()
        # Pass the specific stock data for the given tickers
        X, y, scaler = prepare_lstm_data(stock_data[tickers])  # Use stock_data[tickers] to ensure proper indexing
        timings['prepare_lstm_data'] = time.perf_counter() - start_time

        # Step 5: Build and train the model
        start_time = time.perf_counter()
        model = build_cnn_lstm_model((X.shape[1], X.shape[2]))  # Fix the input shape for Conv1D with multiple features
        timings['build_cnn_lstm_model'] = time.perf_counter() - start_time

        start_time = time.perf_counter()
        model = train_lstm_model(model, X, y)
        timings['train_lstm_model'] = time.perf_counter() - start_time

        # Step 6: Predict stock prices
        start_time = time.perf_counter()
        predictions, future_predictions = predict_stock_prices_lstm(model, stock_data[tickers], scaler)
        timings['predict_stock_prices_lstm'] = time.perf_counter() - start_time

        # Step 7: Save data to DB
        timings['total'] = time.perf_counter() - total_start_time
        save_data_to_db(tickers, period, stock_data, predictions, future_predictions, fundamentals, timings)

        print(timings)
        return stock_data, fundamentals, predictions, future_predictions
