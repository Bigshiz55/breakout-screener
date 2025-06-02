import yfinance as yf
import time
from datetime import datetime
import requests

# --- STEP 1: Your reverse split watchlist (temporary hardcoded list)
split_tickers = ["APDN", "BNRG", "TAOP", "EKSO"]  # Replace this daily or automate later

# --- STEP 2: Your Pushover setup
PUSHOVER_USER_KEY = "your_user_key"
PUSHOVER_API_TOKEN = "your_app_token"

def send_pushover_notification(title, message):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": title,
        "message": message
    }
    requests.post(url, data=data)

# --- STEP 3: Technical indicator helpers
def calculate_macd(data):
    exp12 = data['Close'].ewm(span=12, adjust=False).mean()
    exp26 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd.iloc[-1], signal.iloc[-1]

def calculate_vwap(data):
    vwap = (data['Close'] * data['Volume']).cumsum() / data['Volume'].cumsum()
    return vwap.iloc[-1]

# --- STEP 4: Screener logic
def check_split_ticker(ticker):
    try:
        data = yf.download(ticker, interval="1m", period="1d", progress=False)

        if len(data) < 30:
            return  # Not enough data

        macd, signal = calculate_macd(data)
        macd_cross = macd > signal

        vwap = calculate_vwap(data)
        last_price = data['Close'].iloc[-1]
        vwap_reclaim = last_price > vwap

        avg_volume = data['Volume'].iloc[-30:-5].mean()
        recent_volume = data['Volume'].iloc[-1]
        volume_spike = recent_volume > avg_volume * 2

        print(f"{ticker}: MACD Cross={macd_cross}, VWAP={vwap_reclaim}, Volume Spike={volume_spike}")

        if macd_cross and vwap_reclaim and volume_spike:
            send_pushover_notification(
                f"🚨 Post-Split Setup: {ticker}",
                f"MACD cross, VWAP reclaim, volume spike.\nPrice: {last_price:.2f}"
            )

    except Exception as e:
        print(f"Error with {ticker}: {e}")

# --- STEP 5: Run every minute
while True:
    print(f"\nRunning screener at {datetime.now().strftime('%H:%M:%S')}")
    for ticker in split_tickers:
        check_split_ticker(ticker)
    time.sleep(60)
