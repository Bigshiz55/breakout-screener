import yfinance as yf
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# ==== Pushover Configuration ====
PUSHOVER_USER_KEY = "your_user_key_here"
PUSHOVER_API_TOKEN = "your_api_token_here"

def send_pushover_notification(title, message):
    print(f"Sending Pushover alert: {title} — {message}")

    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": title,
        "message": message
    }

    try:
        response = requests.post(url, data=data)
        print(f"Pushover response code: {response.status_code}")
        print(f"Pushover response text: {response.text}")
    except Exception as e:
        print(f"Pushover error: {e}")

# ==== Auto-Fetch Reverse Splits from Nasdaq ====
def get_recent_reverse_splits():
    url = "https://www.nasdaq.com/market-activity/stocks/splits"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")

        tickers = []
        if table:
            rows = table.find_all("tr")[1:]
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 3:
                    ratio = cols[2].text.strip()
                    if ":" in ratio:
                        a, b = ratio.split(":")
                        if a.isdigit() and b.isdigit() and int(a) > int(b):  # Reverse split
                            ticker = cols[0].text.strip().upper()
                            tickers.append(ticker)
        print(f"Auto-loaded reverse split tickers: {tickers}")
        return tickers
    except Exception as e:
        print(f"Error fetching reverse splits: {e}")
        return []

# ==== Indicator Calculations ====
def calculate_macd(data):
    exp12 = data['Close'].ewm(span=12, adjust=False).mean()
    exp26 = data['Close'].ewm(span=26, adjust=False).mean()
