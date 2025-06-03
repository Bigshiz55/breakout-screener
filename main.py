import os
import requests
import time
import datetime
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.live import StockDataStream

# === Alpaca API keys ===
ALPACA_API_KEY = 'your_alpaca_api_key'
ALPACA_SECRET_KEY = 'your_alpaca_secret_key'
PUSHOVER_USER_KEY = 'your_pushover_user_key'
PUSHOVER_APP_TOKEN = 'your_pushover_app_token'

# === Initialize Alpaca clients ===
client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)

# === List of all NASDAQ tickers ===
nasdaq_tickers = [
    "AAPL", "MSFT", "GOOG", "AMZN", "NVDA", "TSLA", "META", "ADBE", "INTC", "CSCO",
    # Paste your full list of 3300+ tickers here or load from file
]

# === Float values (must be sourced externally and manually updated if using Alpaca only) ===
# Example mock values for testing
ticker_float = {
    "AAPL": 16000000000,
    "MSFT": 7500000000,
    "GOOG": 600000000,
    # Add all floats here
}

# === Pushover Alert Function ===
def send_pushover_notification(title, message):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": title,
        "message": message
    }
    requests.post(url, data=data)

# === Breakout Screener Logic ===
def check_breakout_conditions(ticker):
    try:
        # Pull last 2 days of 1-minute bars
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

        # Volume spike (last bar's volume > 2x average of last 20 bars)
        avg_volume = df['volume'].tail(20).mean()
        current_volume = df['volume'].iloc[-1]
        volume_spike = current_volume > 2 * avg_volume

        # MACD crossover (simplified 12-26 EMA crossover)
        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        macd_now = ema12.iloc[-1] - ema26.iloc[-1]
        macd_prev = ema12.iloc[-2] - ema26.iloc[-2]
        macd_crossover = macd_prev < 0 and macd_now > 0

        # VWAP reclaim (price crosses above VWAP)
        vwap = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
        vwap_reclaim = df['close'].iloc[-2] < vwap.iloc[-2] and df['close'].iloc[-1] > vwap.iloc[-1]

        # Float churn (volume > float)
        day_volume = df['volume'].sum()
        float_churn = ticker_float.get(ticker, float('inf')) > 0 and day_volume >= 2 * ticker_float[ticker]

        if volume_spike and macd_crossover and vwap_reclaim and float_churn:
            message = f"{ticker} breakout:\nVol Spike, MACD Cross, VWAP Reclaim, Float Churn"
            send_pushover_notification("Breakout Alert", message)

    except Exception as e:
        print(f"Error processing {ticker}: {e}")

# === Main Loop ===
def main():
    send_pushover_notification("System Online", "Breakout Screener is running.")
    while True:
        for ticker in nasdaq_tickers:
            check_breakout_conditions(ticker)
            time.sleep(0.2)  # Rate limit control
        print("Batch complete. Sleeping 5 min.")
        time.sleep(300)

if __name__ == "__main__":
    main()
