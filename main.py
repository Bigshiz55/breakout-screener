print("🚨 main.py file loaded...")

import os
import time
import requests
import datetime
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID", "your_alpaca_key_here")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY", "your_alpaca_secret_here")

print("Initializing Alpaca client...")
client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)
print("✅ Alpaca client initialized.")

def send_pushover_notification(title, message):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": "atq27zau5k3caa3tnmfh2cc3e9ru4m",
            "user": "uiyuixjg93r2kbmbhnpfcjfqhmh8s9",
            "title": title,
            "message": message
        },
    )

def get_latest_volume(ticker):
    try:
        request_params = StockBarsRequest(
            symbol_or_symbols=ticker,
            timeframe=TimeFrame.Minute,
            start=datetime.datetime.now() - datetime.timedelta(minutes=15),
        )
        bars = client.get_stock_bars(request_params)
        if bars is None:
            raise ValueError("No data returned from Alpaca")
        if not hasattr(bars, 'df') or bars.df is None or bars.df.empty:
            raise ValueError("Empty or missing dataframe")
        df = bars.df[bars.df.index.get_level_values(0) == ticker]
        if df.empty:
            raise ValueError("No bars found for ticker")
        latest_bar = df.iloc[-1]
        return latest_bar.close, latest_bar.volume
    except Exception as e:
        print(f"Error fetching volume for {ticker}: {e}")
        return None, 0

    try:
        request_params = StockBarsRequest(
            symbol_or_symbols=ticker,
            timeframe=TimeFrame.Minute,
            start=datetime.datetime.now() - datetime.timedelta(minutes=15),
        )
        bars = client.get_stock_bars(request_params)
        if not bars or not hasattr(bars, 'df') or bars.df.empty:
            return None, 0
        df = bars.df[bars.df.index.get_level_values(0) == ticker]
        if df.empty:
            return None, 0
        latest_bar = df.iloc[-1]
        return latest_bar.close, latest_bar.volume
    except Exception as e:
        print(f"Error fetching volume for {ticker}: {e}")
        return None, 0

    try:
        request_params = StockBarsRequest(
            symbol_or_symbols=ticker,
            timeframe=TimeFrame.Minute,
            start=datetime.datetime.now() - datetime.timedelta(minutes=15),
        )
        bars = client.get_stock_bars(request_params).df
        if bars.empty:
            return None, 0
        latest_bar = bars.iloc[-1]
        return latest_bar.close, latest_bar.volume
    except Exception as e:
        print(f"Error fetching volume for {ticker}: {e}")
        return None, 0

def main():
    print("✅ Starting screener...")
    print("✅ Screener online and scanning...")
    send_pushover_notification("Screener Active", "Live scanning all IEX stocks.")

    tickers = [
    "REVB", "SOFI", "PLTR", "SNAP", "CHGG", "NNDM", "BBBYQ", "BNGO", "BBBY", "GPRO", "RIOT", "MARA", "FCEL", "CLOV", "SNDL", "IDEX", "HUT", "BKKT", "UAVS", "CANO", "BRQS", "TRKA", "XELA", "BTBT", "VERB", "FFIE", "GNS"'AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMD', 'INTC', 'META', 'GOOGL', 'AMZN', 'NFLX', 'BABA', 'SOFI', 'PLTR', 'SNAP', 'F', 'GM', 'BAC', 'WFC', 'T', 'XOM']
    last_status = time.time()

    while True:
        for ticker in tickers:
            print(f"Checking {ticker}")
            price, vol = get_latest_volume(ticker)
            if vol > 1000000:  # Example alert threshold
                send_pushover_notification(
                    f"🔥 ATVI Volume Spike",
                    f"ATVI has volume {vol} and price ${price}"
                )
            time.sleep(1.0)

        # Hourly heartbeat
        if time.time() - last_status >= 3600:
            send_pushover_notification("⏰ Screener Alive", "Still scanning IEX stocks.")
            last_status = time.time()

print("🚀 Calling main()...")
if __name__ == "__main__":
    main()
