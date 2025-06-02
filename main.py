import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import time

# === PUSHOVER CONFIG (replace these) ===
PUSHOVER_USER_KEY = "uiyuixjg93r2kbmbhnpfcjfqhmh8s9"
PUSHOVER_API_TOKEN = "atq27zau5k3caa3tnmfh2cc3e9ru4m"

bad_symbols = set()

def send_pushover_notification(title, message):
    try:
        payload = {
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "title": title,
            "message": message
        }
        requests.post("https://api.pushover.net/1/messages.json", data=payload)
        print(f"✅ Pushover sent: {title}")
    except Exception as e:
        print(f"❌ Pushover failed: {e}")

def check_breakouts(ticker_list, label=""):
    global bad_symbols
    for symbol in ticker_list:
        if symbol in bad_symbols:
            continue
        try:
            data = yf.download(symbol, period="5d", interval="5m", progress=False, threads=False)
            if data.empty or len(data) < 50:
                print(f"{label}{symbol}: ❌ No data or too few bars.")
                bad_symbols.add(symbol)
                continue

            close = data["Close"]
            macd_line = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            macd_cross = macd_line.iloc[-2] <= signal_line.iloc[-2] and macd_line.iloc[-1] > signal_line.iloc[-1]

            typical_price = (data["High"] + data["Low"] + data["Close"]) / 3
            vwap = (typical_price * data["Volume"]).cumsum() / data["Volume"].cumsum()
            vwap_reclaim = close.iloc[-1] > vwap.iloc[-1]

            avg_volume = data["Volume"].iloc[-20:-1].mean()
            last_volume = data["Volume"].iloc[-1]
            volume_spike = last_volume > 1.5 * avg_volume

            print(f"{label}{symbol}: MACD={macd_cross}, VWAP={vwap_reclaim}, VOL Spike={volume_spike}")

            if macd_cross and vwap_reclaim:
                message = (
                    f"{symbol} breakout setup:\n"
                    f"MACD: ✅\n"
                    f"VWAP Reclaim: ✅\n"
                    f"Volume Spike: {'✅' if volume_spike else '❌'}"
                )
                send_pushover_notification(f"{label}Breakout: {symbol}", message)

        except Exception as e:
            print(f"{label}{symbol} error: {e}")
            bad_symbols.add(symbol)

def send_test_push():
    send_pushover_notification("✅ Test Message", "Your screener push alert is working!")

# === CLEAN NASDAQ LIST ===
tickers = [
    "AAPL", "MSFT", "GOOG", "AMZN", "NVDA", "META", "TSLA", "PEP", "ADBE", "COST", "NFLX", "AMD", "QCOM",
    "TXN", "INTU", "ISRG", "AMGN", "VRTX", "MU", "CDNS", "FTNT", "CRWD", "PANW", "ROKU", "PLTR", "COIN", "SOFI",
    "DKNG", "PYPL", "PINS", "SNAP", "RBLX", "ETSY", "RUN", "ENPH", "NIO", "XPEV", "LI", "BIDU", "JD", "BABA"
]

reverse_split_tickers = ["APDN", "BNRG", "TAOP", "EKSO"]

# === START ===
print("✅ Screener started...")
send_test_push()

last_checkin = 0

while True:
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')

    print(f"\n🔄 Scan running at {now_str}")
    
    # Only send check-in once every 15 minutes
    if (now.minute % 15 == 0) and (now.minute != last_checkin):
        send_pushover_notification("✅ Screener Check-In", f"Heartbeat at {now_str}")
        last_checkin = now.minute
# === FAKE TEST CASE FOR DEBUGGING ===
send_pushover_notification("🚨 Breakout: TEST", "PLTR breakout setup:\nMACD: ✅\nVWAP Reclaim: ✅\nVolume Spike: ❌")

    check_breakouts(tickers)
    check_breakouts(reverse_split_tickers, label="RS: ")
    time.sleep(60)


