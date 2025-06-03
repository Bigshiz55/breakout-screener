
# main.py
import requests
import yfinance as yf
import time
import os
import json
from bs4 import BeautifulSoup

# Pushover config
PUSHOVER_USER_KEY = "your_user_key_here"
PUSHOVER_API_TOKEN = "your_app_token_here"

# Real NASDAQ tickers (replicated list to simulate 3300 real tickers)
nasdaq_tickers = [
    "AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "NVDA", "META", "INTC", "ADBE", "NFLX",
    "AMD", "CSCO", "PEP", "AVGO", "COST", "TMUS", "TXN", "QCOM", "GILD", "SBUX"
] * 165  # 20 * 165 = ~3300

# Float cache
CACHE_FILE = "float_cache.json"
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r') as f:
        float_cache = json.load(f)
else:
    float_cache = {}

def get_float_from_finviz(ticker):
    try:
        url = "https://finviz.com/quote.ashx?t=" + ticker
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find_all("table", class_="snapshot-table2")[0]
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            for i in range(len(cells)):
                if cells[i].text.strip() == "Float":
                    value = cells[i+1].text.strip()
                    multiplier = 1_000_000 if "M" in value else 1_000_000_000
                    return int(float(value.replace("B", "").replace("M", "")) * multiplier)
    except Exception as e:
        print(f"Error fetching float from Finviz for {ticker}: {e}")
    return None

def get_volume(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if hist.empty or 'Volume' not in hist.columns:
            return None
        return int(hist['Volume'][-1])
    except Exception as e:
        print(f"Error fetching volume for {ticker}: {e}")
        return None

def send_pushover_notification(message):
    data = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": message
    }
    requests.post("https://api.pushover.net/1/messages.json", data=data)

def main():
    triggered = []
    for ticker in nasdaq_tickers:
        if ticker not in float_cache or not isinstance(float_cache[ticker], (int, float)):
            float_val = get_float_from_finviz(ticker)
            if float_val:
                float_cache[ticker] = float_val
                with open(CACHE_FILE, 'w') as f:
                    json.dump(float_cache, f)
            else:
                continue

        volume = get_volume(ticker)
        if volume is None:
            continue

        churn = volume / float_cache[ticker]
        print(f"{ticker}: Volume={volume}, Float={float_cache[ticker]}, Churn={churn:.2f}x")

        if churn >= 2:
            triggered.append(f"{ticker} ({churn:.2f}x)")

        time.sleep(1.5)

    if triggered:
        send_pushover_notification("Float Churn Alert: " + ", ".join(triggered))
    else:
        print("No tickers triggered the 2x float churn threshold.")

if __name__ == "__main__":
    main()
