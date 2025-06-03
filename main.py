import os
import requests
import time
import datetime
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# === User-Specific API Keys ===
ALPACA_API_KEY = 'PK9Q5A5VXR9HZ3K9CQZH'
ALPACA_SECRET_KEY = 'uNgyydMfQj7LDbIzoCNXQ5KEXsPYgvRmOwguv4z6'
PUSHOVER_USER_KEY = 'uqqXxxxxxxxxxxxxxxxxxxxxx'
PUSHOVER_APP_TOKEN = 'az7zxxxxxxxxxxxxxxxxxxxxx'

# === Initialize Alpaca client ===
client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)

# === NASDAQ tickers list (insert full 3300+ list here) ===
nasdaq_tickers = [
    "TRAW", "TOVX", "BURU", "BNRG", "FAAS"  # Add more tickers here
]

# === Manually input known float values ===
ti
