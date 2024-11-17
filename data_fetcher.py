import yfinance as yf
import requests

ALPHA_VANTAGE_API_KEY = 'YOUR_API_KEY_HERE'

def fetch_yahoo_data(tickers, period='1y'):
    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period=period)
        stock_data['SMA_20'] = stock_data['Close'].rolling(window=20).mean()
        stock_data['SMA_50'] = stock_data['Close'].rolling(window=50).mean()
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
