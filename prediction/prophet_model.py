from prophet import Prophet

def predict_stock_prices(stock_data, periods=30):
    df = stock_data.reset_index()[['Date', 'Close']]
    df.columns = ['ds', 'y']

    # Remove timezone information
    df['ds'] = df['ds'].dt.tz_localize(None)

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]


