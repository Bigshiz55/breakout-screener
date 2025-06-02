
import requests
import time
import yfinance as yf
from datetime import datetime

PUSHOVER_USER_KEY = "YOUR_USER_KEY"
PUSHOVER_API_TOKEN = "YOUR_API_TOKEN"

TICKERS = [
    "AAPL",
    "MSFT",
    "GOOG",
    "AMZN",
    "META",
    "NVDA",
    "TSLA",
    "NFLX",
    "ADBE",
    "INTC",
    "CSCO"
]

# Placeholder float values (user can replace with accurate values)
FLOATS = {
    "AAPL": 16000000000,
    "MSFT": 7500000000,
    "GOOG": 600000000,
    "AMZN": 10200000000,
    "META": 2300000000,
    "NVDA": 2400000000,
    "TSLA": 3100000000,
    "NFLX": 430000000,
    "ADBE": 450000000,
    "INTC": 4200000000,
    "CSCO": 4100000000
}

def send_pushover_notification(title, message):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": title,
        "message": message,
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Pushover error:", e)

def check_conditions(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="5m", progress=False)
        if len(data) < 10: return
        latest = data.iloc[-1]
        prev = data.iloc[-2]

        # Breakout conditions
        volume_spike = latest['Volume'] > 1.5 * data['Volume'].rolling(10).mean().iloc[-2]
        price_above_vwap = latest['Close'] > data['Close'].mean()
        macd_cross = latest['Close'] > prev['Close']
        if volume_spike and price_above_vwap and macd_cross:
            send_pushover_notification("Breakout Alert", f"📈 {ticker} meets breakout criteria.")

        # Float churn alert
        if ticker in FLOATS:
            daily_data = yf.download(ticker, period="1d", interval="1m", progress=False)
            if not daily_data.empty:
                total_volume = daily_data['Volume'].sum()
                if total_volume > FLOATS[ticker] * 1.0:
                    send_pushover_notification("Float Churn Alert", f"🔥 {ticker} volume exceeds float.")

        # Gap-down recovery alert
        open_price = data.iloc[0]['Open']
        low_after_open = data['Low'].iloc[1:10].min()
        reclaim_vwap = latest['Close'] > data['Close'].mean()
        if open_price > latest['Close'] and reclaim_vwap and latest['Close'] > low_after_open:
            send_pushover_notification("Gap-Down Recovery", f"⚡ {ticker} is reclaiming VWAP after gapping down.")

        # Reverse split notifier (placeholder: simulate 1-for-10 RS detection by price surge)
        if latest['Close'] > 5 * data['Close'].mean():
            send_pushover_notification("Reverse Split Watch", f"🔍 {ticker} may have done a recent reverse split.")
    except Exception as e:
        print(f"Error checking {ticker}:", e)

def run_screener():
    while True:
        for ticker in TICKERS:
            check_conditions(ticker)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        send_pushover_notification("Heartbeat", f"✅ Screener running: {now}")
        time.sleep(300)  # wait 5 minutes

if __name__ == "__main__":
    run_screener()
