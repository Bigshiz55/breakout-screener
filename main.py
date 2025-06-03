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
PUSHOVER_USER_KEY = 'uiyuixjg93r2kbmbhnpfcjfqhmh8s9'
PUSHOVER_APP_TOKEN = 'atq27zau5k3caa3tnmfh2cc3e9ru4m'

client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)

# === Safe Tickers ===
nasdaq_tickers = [
    "TRAW", "TOVX", "BURU", "BNRG", "FAAS", "ROKU", "DOCU", "SNOW", "PLTR", "UBER",
    "LYFT", "CVNA", "PDD", "ILMN", "EXPE", "SIRI", "CHTR", "EA", "WBD", "MAR", "ATVI"
]

# === Float values ===
ticker_float = {
    "TRAW": 4520000,
    "TOVX": 8100000,
    "BURU": 2900000,
    "BNRG": 3400000,
    "FAAS": 3800000
}

def send_pushover_notification(title, message):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": title,
        "message": message
    }
    print(f"Sending Pushover alert: {title} – {message}")
    requests.post(url, data=data)

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

        avg_vol = df['volume'].tail(20).mean()
        last_vol = df['volume'].iloc[-1]
        volume_spike = last_vol > 2 * avg_vol

        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        macd_now = ema12.iloc[-1] - ema26.iloc[-1]
        macd_prev = ema12.iloc[-2] - ema26.iloc[-2]
        macd_cross = macd_prev < 0 and macd_now > 0

        vwap = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
        vwap_reclaim = df['close'].iloc[-2] < vwap.iloc[-2] and df['close'].iloc[-1] > vwap.iloc[-1]

        total_volume = df['volume'].sum()
        flt = ticker_float.get(ticker, float('inf'))
        float_churn = flt > 0 and total_volume >= 2 * flt

        # === Primary Alert ===
        if volume_spike and macd_cross and vwap_reclaim and float_churn:
            message = f"{ticker} breakout:\nVol Spike, MACD Cross, VWAP Reclaim, Float Churn"
            send_pushover_notification("Breakout Alert", message)

        # === Secondary Float-Only Alert ===
        elif volume_spike and float_churn:
            message = f"{ticker} float alert:\nVol Spike + Float ≥ 2x"
            send_pushover_notification("Float Alert", message)

    except Exception as e:
        print(f"Error with {ticker}: {e}")

def main():
    print("Starting main loop...")
    send_pushover_notification("System Online", "Breakout screener is live and scanning.")
    last_ping = time.time()

    while True:
        for ticker in nasdaq_tickers:
            print(f"Checking {ticker}")
            check_breakout_conditions(ticker)
            time.sleep(1.0)

        now = time.time()
        if now - last_ping >= 3600:
            send_pushover_notification("Still Running", "✅ Breakout screener is active. No breakouts in the past hour.")
            last_ping = now

        print("Batch complete. Sleeping 5 minutes.")
        print("---")
        time.sleep(300)

if __name__ == "__main__":
    main()
