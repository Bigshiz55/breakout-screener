import os
import time
import requests
import yfinance as yf
import pandas as pd
from ta.trend import MACD
from ta.volume import OnBalanceVolumeIndicator

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

# Starter ticker list (we'll automate this later)
tickers_to_watch = [
    "QBTS", "FAAS", "BTOG", "SINT", "ABP", "GNS", "ATXG", "HCDI", "TOP", "SGBX",
    "YOSH", "UCAR", "IMNN", "TAOP", "EJH", "HUDI", "ILAG", "JXJT", "MGOL", "TGL"
]

def meets_breakout_conditions(df):
    # Ensure enough data
    if len(df) < 35:
        return False

    # Calculate MACD
    macd = MACD(df["Close"])
    df["macd_diff"] = macd.macd_diff().squeeze()

    # Volume spike check
    recent_vol = df["Volume"].iloc[-1]
    avg_vol = df["Volume"].rolling(window=20).mean().iloc[-2]
    vol_spike = recent_vol > avg_vol * 1.5

    # MACD crossover check
    macd_crossover = df["macd_diff"].iloc[-1] > 0 and df["macd_diff"].iloc[-2] <= 0

    # Basic VWAP reclaim (using simple avg close here for now)
    vwap_reclaim = df["Close"].iloc[-1] > df["Close"].mean()

    return vol_spike and macd_crossover and vwap_reclaim

def check_breakouts(tickers):
    print("🧠 Screener is scanning...")
    df_all = yf.download(tickers, period="1d", interval="1m", group_by="ticker", progress=False)
    for ticker in tickers:
        try:
            df = df_all[ticker]
            if meets_breakout_conditions(df):
                price = df["Close"].iloc[-1]
                message = f"{ticker} breakout! Price: ${price:.2f}"
                print(message)
                send_pushover_notification(message)
        except Exception as e:
            print(f"Error with {ticker}: {e}")

# MAIN LOOP
print("📈 Breakout screener is LIVE")
while True:
    check_breakouts(tickers_to_watch)
    time.sleep(60)
