from dash import html


def display_fundamentals(fundamentals, selected_ticker):
    return html.Div(
        [
            html.H5(f"Fundamentals for {selected_ticker}"),
            html.P(f"Market Cap: {fundamentals['Market Cap']}"),
            html.P(f"P/E Ratio: {fundamentals['P/E Ratio']}"),
            html.P(f"Beta: {fundamentals['Beta']}"),
            html.P(f"Dividend Yield: {fundamentals['Dividend Yield']}"),
            html.P(f"Sector: {fundamentals['Sector']}"),
            html.P(f"Industry: {fundamentals['Industry']}"),
            html.P(f"Exchange: {fundamentals['Exchange']}"),
            html.P(f"Currency: {fundamentals['Currency']}"),
            html.P(f"Country: {fundamentals['Country']}"),
            html.P(f"Analyst Target Price: {fundamentals['Analyst Target Price']}"),
        ]
    )
