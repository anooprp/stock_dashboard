import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from layout import create_layout
from graph import prepare_graph_data
import pandas as pd
from data_fetcher import fetch_stock_data,initialize_database
from fundamentals import display_fundamentals

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the list of tickers (you can add more tickers)
tickers = ["AAPL", "GOOG", "MSFT"]

# Set the layout of the app
app.layout = create_layout()

# Initialize the database
initialize_database()

@app.callback(
    [Output('stock-price-graph', 'figure'),
     Output('fundamentals', 'children'),
     Output('selected-period', 'data'),
     Output('selected-period-display', 'children'),
     Output('3mo-button', 'className'),
     Output('6mo-button', 'className'),
     Output('1y-button', 'className'),
     Output('2y-button', 'className'),
     Output('5y-button', 'className'),
     Output('ytd-button', 'className')],
    [Input('3mo-button', 'n_clicks'),
     Input('6mo-button', 'n_clicks'),
     Input('1y-button', 'n_clicks'),
     Input('2y-button', 'n_clicks'),
     Input('5y-button', 'n_clicks'),
     Input('ytd-button', 'n_clicks')],
    [State('ticker-input', 'value'),
     State('selected-period', 'data')]
)
def update_graph_and_fundamentals_on_refresh(n_clicks_3mo, n_clicks_6mo, n_clicks_1y, n_clicks_2y, n_clicks_5y, n_clicks_ytd, selected_ticker, current_period):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == '3mo-button':
        selected_period = '3mo'
        period_text = "3 Months"
    elif button_id == '6mo-button':
        selected_period = '6mo'
        period_text = "6 Months"
    elif button_id == '1y-button':
        selected_period = '1y'
        period_text = "1 Year"
    elif button_id == '2y-button':
        selected_period = '2y'
        period_text = "2 Years"
    elif button_id == '5y-button':
        selected_period = '5y'
        period_text = "5 Years"
    elif button_id == 'ytd-button':
        selected_period = 'ytd'
        period_text = "Year to Date"
    else:
        selected_period = current_period
        period_text = "1 Year"  # Default text

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

    # Determine button classes
    button_classes = {
        '3mo-button': 'me-1 period-button active' if selected_period == '3mo' else 'me-1 period-button',
        '6mo-button': 'me-1 period-button active' if selected_period == '6mo' else 'me-1 period-button',
        '1y-button': 'me-1 period-button active' if selected_period == '1y' else 'me-1 period-button',
        '2y-button': 'me-1 period-button active' if selected_period == '2y' else 'me-1 period-button',
        '5y-button': 'me-1 period-button active' if selected_period == '5y' else 'me-1 period-button',
        'ytd-button': 'me-1 period-button active' if selected_period == 'ytd' else 'me-1 period-button'
    }

    # Return graph, fundamentals, selected period, period text, and button classes
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
    }, fundamentals_display, selected_period, f"Selected Period: {period_text}", button_classes['3mo-button'], button_classes['6mo-button'], button_classes['1y-button'], button_classes['2y-button'], button_classes['5y-button'], button_classes['ytd-button']

if __name__ == '__main__':
    app.run_server(debug=True)