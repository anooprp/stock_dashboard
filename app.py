import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from layout import create_layout
from graph import prepare_graph_data
#from prediction.lstm import *
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

    # Fetch stock data and predictions
    stock_data, fundamentals, predictions, future_predictions = fetch_stock_data(selected_ticker, selected_period)

    # Prepare the graph data
    graph_data = prepare_graph_data(stock_data)
    print('Enhancing graph data')

    # Add historical close prices
    graph_data.append(go.Scatter(
        x=stock_data[selected_ticker].index,
        y=stock_data[selected_ticker]['Close'],
        mode='lines',
        name='Historical Close',
        line=dict(color='blue', width=2)
    ))

    # Add moving averages
    graph_data.append(go.Scatter(
        x=stock_data[selected_ticker].index,
        y=stock_data[selected_ticker]['SMA_20'],
        mode='lines',
        name='SMA 20',
        line=dict(color='green', width=1, dash='dot')
    ))
    graph_data.append(go.Scatter(
        x=stock_data[selected_ticker].index,
        y=stock_data[selected_ticker]['SMA_50'],
        mode='lines',
        name='SMA 50',
        line=dict(color='red', width=1, dash='dot')
    ))

    # Add golden buy points
    for i in range(1, len(stock_data[selected_ticker])):
        if (stock_data[selected_ticker]['SMA_20'].iloc[i] > stock_data[selected_ticker]['SMA_50'].iloc[i] and
                stock_data[selected_ticker]['SMA_20'].iloc[i - 1] <= stock_data[selected_ticker]['SMA_50'].iloc[i - 1]):
            graph_data.append(go.Scatter(
                x=[stock_data[selected_ticker].index[i]],
                y=[stock_data[selected_ticker]['Close'].iloc[i]],
                mode='markers',
                marker=dict(color='gold', size=10),
                name='Golden Buy Point'
            ))

    # Add predicted close prices
    graph_data.append(go.Scatter(
        x=stock_data[selected_ticker].index[-len(predictions):],
        y=predictions.flatten(),
        mode='lines',
        name='Predicted Close',
        line=dict(color='purple', width=2, dash='dash')
    ))

    # Add future predictions
    future_dates = pd.date_range(
        start=stock_data[selected_ticker].index[-1],
        periods=len(future_predictions) + 1,
        freq='B'  # Business days
    )
    graph_data.append(go.Scatter(
        x=future_dates[1:],  # Skip the first date to align with future predictions
        y=future_predictions.flatten(),
        mode='lines',
        name='Future Predictions',
        line=dict(color='orange', width=2, dash='dash')
    ))

    # Prepare fundamentals display
    fundamentals_display = display_fundamentals(fundamentals, selected_ticker)
    print('prepared fundamentals and created the chart')

    # Return graph and fundamentals
    return {
        'data': graph_data,
        'layout': go.Layout(
            title=f'{selected_ticker} Stock Price, Moving Averages, and Predictions',
            xaxis_title='Date',
            yaxis_title='Price',
            template='plotly_white',
            legend=dict(orientation="h", x=0, y=-0.2),
            margin=dict(l=40, r=40, t=40, b=40),
        )
    }, fundamentals_display


if __name__ == '__main__':
    app.run_server(debug=True)