import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from layout import create_layout
from graph import prepare_graph_data
from prediction.lstm import *
from data_fetcher import  *
from fundamentals import display_fundamentals

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the list of tickers (you can add more tickers)
tickers = ["AAPL", "GOOG", "MSFT"]

# Set the layout of the app
app.layout = create_layout(tickers)

# Initialize the database
initialize_database()

@app.callback(
    Output('stock-price-graph', 'figure'),
    Output('fundamentals', 'children'),
    [Input('refresh-button', 'n_clicks')],
    [State('ticker-input', 'value'),
     State('time-period-dropdown', 'value')]
)
def update_graph_and_fundamentals_on_refresh(n_clicks, selected_ticker, selected_period):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    stock_data, fundamentals = fetch_stock_data(selected_ticker, selected_period)

    # Prepare the graph data
    graph_data = prepare_graph_data([selected_ticker], selected_period)

    # Identify golden buy points
    golden_buy_points = []
    for i in range(1, len(stock_data[selected_ticker])):
        if (stock_data[selected_ticker]['SMA_20'].iloc[i] > stock_data[selected_ticker]['SMA_50'].iloc[i] and
                stock_data[selected_ticker]['SMA_20'].iloc[i - 1] <= stock_data[selected_ticker]['SMA_50'].iloc[i - 1]):
            golden_buy_points.append(go.Scatter(
                x=[stock_data[selected_ticker].index[i]],
                y=[stock_data[selected_ticker]['Close'].iloc[i]],
                mode='markers',
                marker=dict(color='gold', size=10),
                name='Golden Buy Point'
            ))

    graph_data.extend(golden_buy_points)

    # Prepare data for LSTM model
    X, y, scaler = prepare_lstm_data(stock_data[selected_ticker])
    model = build_cnn_lstm_model((X.shape[1], 1))
    model = train_lstm_model(model, X, y)

    # Predict future stock prices
    predictions, future_predictions = predict_stock_prices_lstm(model, stock_data[selected_ticker], scaler)

    # Add predicted close prices
    graph_data.append(go.Scatter(
        x=stock_data[selected_ticker].index[-len(predictions):],
        y=predictions.flatten(),
        mode='lines',
        name='Predicted Close',
        line=dict(color='purple', width=2, dash='dash')
    ))

    # Add future predictions
    future_dates = pd.date_range(start=stock_data[selected_ticker].index[-1], periods=len(future_predictions) + 1)
    graph_data.append(go.Scatter(
        x=future_dates[1:],  # Skip the first date to align with future predictions
        y=future_predictions.flatten(),
        mode='lines',
        name='Future Predictions',
        line=dict(color='orange', width=2, dash='dash')
    ))

    # Display fundamentals
    fundamentals_display = display_fundamentals(fundamentals, selected_ticker)

    return {
               'data': graph_data,
               'layout': {
                   'title': f'{selected_ticker} Stock Price, Moving Averages, and Predictions'
               }
           }, fundamentals_display

if __name__ == '__main__':
    app.run_server(debug=True)