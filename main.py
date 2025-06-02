import yfinance as yf
import time
import requests
import datetime

# === PUSHOVER CONFIG ===
PUSHOVER_USER_KEY = "uiyuixjg93r2kbmbhnpfcjfqhmh8s9"
PUSHOVER_API_TOKEN = "atq27zau5k3caa3tnmfh2cc3e9ru4m"

def send_pushover_notification(message):
    requests.post("https://api.pushover.net/1/messages.json", data={
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": message
    })

def fetch_data(ticker):
    try:
        data = yf.download(ticker, period="5d", interval="5m", progress=False)
        return data
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def calculate_macd(data):
    exp1 = data["Close"].ewm(span=12, adjust=False).mean()
    exp2 = data["Close"].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def check_breakouts(tickers):
    for ticker in tickers:
        data = fetch_data(ticker)
        if data is None or len(data) < 35:
            continue
        vwap = (data["Close"] * data["Volume"]).cumsum() / data["Volume"].cumsum()
        macd, signal = calculate_macd(data)

        # Strict bullish logic: MACD crossover just occurred & VWAP reclaimed
        if (
            macd.iloc[-2] < signal.iloc[-2] and
            macd.iloc[-1] > signal.iloc[-1] and
            data["Close"].iloc[-1] > vwap.iloc[-1]
        ):
            send_pushover_notification(f"📈 Breakout Alert: {ticker} — MACD Bullish Crossover & VWAP Reclaimed")

def send_heartbeat():
    now = datetime.datetime.now().strftime("%H:%M:%S")
    send_pushover_notification(f"✅ Screener check-in at {now}")

# === TICKER LIST ===
tickers = [
    "G",
    "H",
    "M",
    "X"
]

# === MAIN LOOP ===
if __name__ == "__main__":
    while True:
        check_breakouts(tickers)
        send_heartbeat()
        time.sleep(900)  # every 15 minutes
