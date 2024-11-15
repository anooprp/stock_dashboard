from dash import html,dcc
def create_layout(tickers):
    return html.Div([
        dcc.Input(
            id='ticker-input',
            type='text',
            placeholder='Enter ticker symbol...',
            value='AAPL'  # Default value
        ),
        dcc.Dropdown(
            id='time-period-dropdown',
            options=[
                {'label': '1 Month', 'value': '1mo'},
                {'label': '3 Months', 'value': '3mo'},
                {'label': '6 Months', 'value': '6mo'},
                {'label': '1 Year', 'value': '1y'},
                {'label': '2 Years', 'value': '2y'},
                {'label': '5 Years', 'value': '5y'},
                {'label': 'YTD', 'value': 'ytd'},
                {'label': 'Max', 'value': 'Max'}
            ],
            value='1y'
        ),
        dcc.Graph(id='stock-price-graph'),
        html.Div(id='fundamentals')
    ])
