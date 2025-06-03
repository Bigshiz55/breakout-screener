
import yfinance as yf
import csv
import time
import requests

# === PUSHOVER CONFIG ===
PUSHOVER_USER_KEY = "68e470305bd4416d41d49a147c06e392290f5561b2b05251264ae41ebabaee6c"
PUSHOVER_APP_TOKEN = "aapx9m3p1rxq7i38c5xwjqfukkyzi6"

# === NASDAQ SAMPLE TICKERS ===
tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META",
    "TSLA", "PEP", "ADBE", "NFLX", "AMD", "CSCO",
    "AVGO", "COST", "TMUS"
]

def send_pushover_alert(ticker, current, avg, spike):
    message = f"🚨 {ticker} volume spike!\nCurrent: {current:,}\nAvg: {avg:,}\nSpike: {spike}x"
    data = {
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": message,
        "title": f"Volume Spike Alert: {ticker}"
    }
    try:
        requests.post("https://api.pushover.net/1/messages.json", data=data)
    except Exception as e:
        print(f"Failed to send alert for {ticker}: {e}")

def fetch_volume_spike(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current_volume = info.get('volume')
        avg_volume = info.get('averageVolume')
        if current_volume is None or avg_volume is None:
            return None, None, None
        spike = round(current_volume / avg_volume, 2) if avg_volume > 0 else None
        return current_volume, avg_volume, spike
    except Exception:
        return None, None, None

with open("volume_spike_report.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Ticker", "Current Volume", "Avg Volume", "Volume Spike (x)"])

    for ticker in tickers:
        current, avg, spike = fetch_volume_spike(ticker)
        if current is None:
            print(f"{ticker}: Data unavailable.")
            continue

        print(f"{ticker}: Current={current}, Avg={avg}, Spike={spike}")
        writer.writerow([ticker, current, avg, spike])

        if spike is not None and spike >= 2.0:
            send_pushover_alert(ticker, current, avg, spike)

        time.sleep(1)

print("Done. CSV saved. Alerts sent for 2x+ spikes.")
