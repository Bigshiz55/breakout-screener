import os
import time
import requests
import yfinance as yf
import pandas as pd
from ta.trend import MACD
from ta.volume import OnBalanceVolumeIndicator

# Load tickers from CSV file
ticker_file = "Nas.csv"
if not os.path.exists(ticker_file):
    raise FileNotFoundError("⚠️ Nas.csv file not found in root directory!")

tickers_df = pd.read_csv(ticker_file)
tickers_to_watch = tickers_df["Symbol"].dropna().unique().tolist()

# Pushover function
def send_pushover_notification(message):
    user_key = os.getenv("PUSHOVER_USER_KEY")
    app_token = os.getenv("PUSHOVER_APP_TOKEN")
    if not user_key or not app_token:
        print("Missing Pushover credentials")
        return
    data = {
        "token": app_token,
        "user": user_key,
        "message": message,
    }
    response = requests.post("https://api.pushover.net/1/messages.json", data=data)
    if response.status_code != 200:
        print(f"Error sending notification: {response.text}")
    else:
        print("✅ Notification sent!")

def meets_breakout_conditions(df):
    if len(df) < 35:
        return False
    macd = MACD(df["Close"])
    df["macd_diff"] = macd.macd_diff()
    vol_now = df["Volume"].iloc[-1]
    vol_avg = df["Volume"].rolling(20).mean().iloc[-2]
    vol_spike = vol_now > vol_avg * 1.5
    macd_cross = df["macd_diff"].iloc[-1] > 0 and df["macd_diff"].iloc[-2] <= 0
    vwap_reclaim = df["Close"].iloc[-1] > df["Close"].mean()
    return vol_spike and macd_cross and vwap_reclaim

def check_breakouts(tickers):
    print("🧠 Scanning for breakouts...")
    df_all = yf.download(tickers, period="1d", interval="1m", group_by="ticker", progress=False, threads=True)
    for ticker in tickers:
        try:
            df = df_all[ticker]
            if meets_breakout_conditions(df):
                price = df["Close"].iloc[-1]
                msg = f"{ticker} breakout! Price: ${price:.2f}"
                print(msg)
                send_pushover_notification(msg)
        except Exception as e:
            print(f"❌ {ticker}: {e}")

# MAIN LOOP
print("📈 Breakout Screener Running...")
while True:
    check_breakouts(tickers_to_watch)
    time.sleep(60)
