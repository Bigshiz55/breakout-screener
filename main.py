import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import time

# === PUSHOVER CONFIG ===
PUSHOVER_USER_KEY = "your_user_key"
PUSHOVER_API_TOKEN = "your_app_token"

def send_pushover_notification(title, message):
    try:
        payload = {
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "title": title,
            "message": message
        }
        response = requests.post("https://api.pushover.net/1/messages.json", data=payload)
        print(f"Pushover sent: {title}")
    except Exception as e:
        print(f"❌ Pushover failed: {e}")

# === BREAKOUT SCANNER LOGIC ===
def check_breakouts(ticker_list, label=""):
    for symbol in ticker_list:
        try:

