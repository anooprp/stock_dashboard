import plotly.graph_objs as go


def prepare_graph_data(stock_data_dict):
    data = []
    print("inside prepare_graph_data")
    for ticker, stock_data in stock_data_dict.items():
        try:
            # Stock price trace
            data.append(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data["Close"],
                    mode="lines",
                    name=f"{ticker} Close",
                    line=dict(color="blue", width=2),
                )
            )

            # 20-day SMA trace
            data.append(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data["SMA_20"],
                    mode="lines",
                    name=f"{ticker} 20-day SMA",
                    line=dict(color="green", width=1, dash="dot"),
                )
            )

            # 50-day SMA trace
            data.append(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data["SMA_50"],
                    mode="lines",
                    name=f"{ticker} 50-day SMA",
                    line=dict(color="red", width=1, dash="dot"),
                )
            )

            # Identify golden buy points
            golden_buy_points = []
            for i in range(1, len(stock_data)):
                if (
                    stock_data["SMA_20"].iloc[i] > stock_data["SMA_50"].iloc[i]
                    and stock_data["SMA_20"].iloc[i - 1]
                    <= stock_data["SMA_50"].iloc[i - 1]
                ):
                    golden_buy_points.append(
                        go.Scatter(
                            x=[stock_data.index[i]],
                            y=[stock_data["Close"].iloc[i]],
                            mode="markers",
                            marker=dict(color="gold", size=10),
                            name="Golden Buy Point",
                        )
                    )

            # Add golden buy points to the data
            data.extend(golden_buy_points)

        except Exception as e:
            print(f"Error processing data for {ticker}: {e}")

    return data
