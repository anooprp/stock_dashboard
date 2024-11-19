import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, LSTM, Dense, Dropout


def prepare_lstm_data(stock_data, time_step=60):
    data = stock_data["Close"].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    X, y = [], []
    for i in range(time_step, len(scaled_data)):
        X.append(scaled_data[i - time_step : i, 0])
        y.append(scaled_data[i, 0])

    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    return X, y, scaler


def build_cnn_lstm_model(input_shape):
    model = Sequential()
    model.add(
        Conv1D(filters=64, kernel_size=3, activation="relu", input_shape=input_shape)
    )
    model.add(MaxPooling1D(pool_size=2))
    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))

    model.compile(optimizer="adam", loss="mean_squared_error")
    return model


def train_lstm_model(model, X_train, y_train, epochs=50, batch_size=32):
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1)
    return model


def predict_stock_prices_lstm(model, stock_data, scaler, time_step=60, periods=30):
    data = stock_data["Close"].values.reshape(-1, 1)
    scaled_data = scaler.transform(data)

    X_test = []
    for i in range(time_step, len(scaled_data)):
        X_test.append(scaled_data[i - time_step : i, 0])

    X_test = np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions)

    future_predictions = []
    last_data = scaled_data[-time_step:]
    for _ in range(periods):
        pred = model.predict(np.reshape(last_data, (1, time_step, 1)))
        future_predictions.append(pred[0, 0])
        last_data = np.append(last_data[1:], pred)

    future_predictions = scaler.inverse_transform(
        np.array(future_predictions).reshape(-1, 1)
    )

    return predictions, future_predictions
