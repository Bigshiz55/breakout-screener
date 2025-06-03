import os
import requests
import time
import datetime
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# === API Keys ===
ALPACA_API_KEY = 'PK9Q5A5VXR9HZ3K9CQZH'
ALPACA_SECRET_KEY = 'uNgyydMfQj7LDbIzoCNXQ5KEXsPYgvRmOwguv4z6'
PUSHOVER_USER_KEY = 'uqqXxxxxxxxxxxxxxxxxxxxxx'
PUSHOVER_APP_TOKEN = 'az7zxxxxxxxxxxxxxxxxxxxxx'

client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)

# === NASDAQ Tickers (truncated list for space – full list should be inserted here) ===
nasdaq_tickers = [
    "AAPL", "MSFT", "GOOG", "AMZN", "NVDA", "TSLA", "META", "ADBE", "INTC", "CSCO",
    "TRAW", "TOVX", "BURU", "BNRG", "FAAS",  # Your focus tickers
    # ... include rest of 3300 tickers here ...
]

# === Known float values (example, update as needed) ===
ticker_float = {
    "TRAW": 4520000,
    "TOVX": 8100000,
    "BURU": 2900000,
    "BNRG": 3400000,
    "FAAS": 3800000,
    # Add more tickers + floats here
}

# === Send Pushover Notification ===
def send_pushover_notification(title, message):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": title,
        "message": message
    }
    requests.post(url, data=data)

# === Check breakout conditions ===
def check_breakout_conditions(ticker):
    try:
        request_params = StockBarsRequest(
            symbol_or_symbols=ticker,
            timeframe=TimeFrame.Minute,
            start=datetime.datetime.now() - datetime.timedelta(days=2),
            end=datetime.datetime.now()
        )
        bars = client.get_stock_bars(request_params).df

        if bars.empty:
            return

        df = bars[bars.index.get_level_values(0) == ticker]
        if df.empty or len(df) < 30:
            return

        # Volume spike
        avg_vol = df['volume'].tail(20).mean()
        last_vol = df['volume'].iloc[-1]
        volume_spike = last_vol > 2 * avg_vol

        # MACD crossover
        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        macd_now = e_
