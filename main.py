import os
import time
import requests
import yfinance as yf
import pandas as pd
import ta

# Load credentials from environment variables
USER_KEY = os.getenv("PUSHOVER_USER_KEY")
APP_TOKEN = os.getenv("PUSHOVER_APP_TOKEN")

def send_notification(message):
    if not USER_KEY or not APP_TOKEN:
        print("Missing credentials")
        return
    data = {"token": APP_TOKEN, "user": USER_KEY, "message": message}
    r = requests.post("https://api.pushover.net/1/messages.json", data=data)
    print("✅ Notification sent!" if r.status_code == 200 else f"Error: {r.text}")

# Core breakout scan
def check_breakouts(tickers):
    for ticker in tickers:
        df = yf.download(ticker, period="2d", interval="1m")
        if df.empty or len(df) < 35:
            continue

        df['volume_sma20'] = df['Volume'].rolling(20).mean()
        macd = ta.trend.MACD(df['Close'])
      df['macd_diff'] = macd.macd_diff().squeeze()
        df['vwap'] = ta.volume.volume_weighted_average_price(df['High'], df['Low'], df['Close'], df['Volume'])

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        conditions = [
            latest['Close'] > latest['vwap'],                         # VWAP Reclaim
            latest['macd_diff'] > 0 and prev['macd_diff'] < 0,       # MACD Crossover
            latest['Volume'] > 1.5 * latest['volume_sma20'],         # Volume Spike
        ]

        if all(conditions):
            send_notification(f"{ticker} breakout! Price: ${latest['Close']:.2f}")

# Replace with your own watchlist
tickers_to_watch = [
    "FAAS", "QBTS", "NVNI", "XAGE", "ABP", "BTOG", "BNRG", "ATXG", "TAOP",
    # add more tickers here
]

print("📈 Screener is running...")
while True:
    check_breakouts(tickers_to_watch)
    time.sleep(60)
