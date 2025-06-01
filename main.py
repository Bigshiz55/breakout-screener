import requests
import os

import requests
import os
import time
import yfinance as yf

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

# === YOUR BREAKOUT CONDITIONS ===
# Set your target stock and breakout parameters
TICKER = "FAAS"
THRESHOLD_PRICE = 3.50  # Alert if price crosses this
INTERVAL_SECONDS = 60   # Check every 60 seconds

def check_price():
    stock = yf.Ticker(TICKER)
    data = stock.history(period="1d", interval="1m")
    if data.empty:
        print("No data available")
        return

    current_price = data["Close"].iloc[-1]
    print(f"{TICKER} current price: {current_price}")

    if current_price > THRESHOLD_PRICE:
        send_pushover_notification(f"{TICKER} is breaking out! Price: ${current_price:.2f}")

print("📈 Breakout screener is running...")

while True:
    check_price()
    time.sleep(INTERVAL_SECONDS)

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
        print("Notification sent!")

# Trigger a test notification
send_pushover_notification("Breakout Screener is now LIVE!")
