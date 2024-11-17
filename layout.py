from dash import dcc, html
import dash_bootstrap_components as dbc

def create_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Stock Dashboard", className='text-center mb-4'), width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Label("Enter Ticker:"),
                dcc.Input(
                    id='ticker-input',
                    type='text',
                    value='AAPL',  # Default value
                    debounce=True,
                    placeholder='Enter ticker symbol...',
                    className='form-control'
                ),
            ], width=3),
            dbc.Col([
                html.Label("Select Time Period:"),
                html.Div(id='selected-period-display', className='mt-2 ms-3'),
                html.Div([
                    dbc.Button("3 Months", id='3mo-button', color="primary", className="me-1 period-button"),
                    dbc.Button("6 Months", id='6mo-button', color="primary", className="me-1 period-button"),
                    dbc.Button("1 Year", id='1y-button', color="primary", className="me-1 period-button"),
                    dbc.Button("2 Years", id='2y-button', color="primary", className="me-1 period-button"),
                    dbc.Button("5 Years", id='5y-button', color="primary", className="me-1 period-button"),
                    dbc.Button("YTD", id='ytd-button', color="primary", className="me-1 period-button")
                ], className='d-flex flex-wrap')
            ], width=9)
        ], className='mb-4'),
        dbc.Row([
            dbc.Col([
                dcc.Loading(
                    id="loading-graph",
                    type="default",
                    children=dcc.Graph(id='stock-price-graph')
                )
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='fundamentals', className='mt-4'), width=12)
        ]),
        dcc.Store(id='selected-period', data='1y')  # Default period
    ], fluid=True)