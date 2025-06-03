import requests
from alpaca.data.historical import StockHistoricalDataClient

ALPACA_API_KEY = 'PK9Q5A5VXR9HZ3K9CQZH'
ALPACA_SECRET_KEY = 'uNgyydMfQj7LDbIzoCNXQ5KEXsPYgvRmOwguv4z6'
PUSHOVER_USER_KEY = 'uiyuixjg93r2kbmbhnpfcjfqhmh8s9'
PUSHOVER_APP_TOKEN = 'atq27zau5k3caa3tnmfh2cc3e9ru4m'

def send_pushover_notification(title, message):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": title,
        "message": message
    }
    print(f"Sending Pushover: {title} – {message}")
    requests.post(url, data=data)

print("Step 1: Starting Alpaca client...")
try:
    client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)
    print("✅ Alpaca client initialized.")
except Exception as e:
    print(f"❌ Alpaca init failed: {e}")

print("Step 2: Sending test notification...")
try:
    send_pushover_notification("Diagnostic Test", "✅ main.py reached and executed.")
    print("✅ Pushover alert sent.")
except Exception as e:
    print(f"❌ Pushover failed: {e}")
