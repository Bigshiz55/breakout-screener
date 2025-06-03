
import os
import time
import requests
import datetime
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID", "your_alpaca_key_here")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY", "your_alpaca_secret_here")

client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)

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
        bars = client.get_stock_bars(request_params).df
        if bars.empty:
            return None, 0
        latest_bar = bars.iloc[-1]
        return latest_bar.close, latest_bar.volume
    except Exception as e:
        print(f"Error fetching volume for {ticker}: {e}")
        return None, 0

def main():
    print("✅ Screener online and scanning...")
    send_pushover_notification("Screener Active", "Live scanning all IEX stocks.")

    tickers = ['AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMD', 'INTC', 'META', 'GOOGL', 'AMZN', 'NFLX', 'BABA', 'SOFI', 'PLTR', 'SNAP', 'F', 'GM', 'BAC', 'WFC', 'T', 'XOM']
    last_status = time.time()

    while True:
        for ticker in tickers:
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

if __name__ == "__main__":
    main()
