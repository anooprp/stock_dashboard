from dash import dcc, html
def create_layout(tickers):
    return html.Div([
        html.H1("Stock Dashboard", style={'textAlign': 'center'}),
        html.Div([
            html.Label("Select Ticker:"),
            dcc.Dropdown(
                id='ticker-input',
                options=[{'label': ticker, 'value': ticker} for ticker in tickers],
                value=tickers[0]
            ),
        ], style={'width': '25%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Select Time Period:"),
            dcc.Dropdown(
                id='time-period-dropdown',
                options=[
                    {'label': '1 Month', 'value': '1mo'},
                    {'label': '3 Months', 'value': '3mo'},
                    {'label': '6 Months', 'value': '6mo'},
                    {'label': '1 Year', 'value': '1y'},
                    {'label': '2 Years', 'value': '2y'},
                    {'label': '5 Years', 'value': '5y'},
                    {'label': 'YTD', 'value': 'ytd'}
                ],
                value='1y'  # Default value
            ),
        ], style={'width': '25%', 'display': 'inline-block'}),
        html.Div(id='fundamentals', style={'marginTop': '20px'}),
        dcc.Graph(id='stock-price-graph'),
        html.Button('Refresh', id='refresh-button', style={'marginTop': '20px'}),
    ])
