import yfinance as yf
import time
import pandas as pd
import requests

# ==== Pushover Configuration ====
PUSHOVER_USER_KEY = "uiyuixjg93r2kbmbhnpfcjfqhmh8s9"
PUSHOVER_API_TOKEN = "a1tg7ugcknh8tv7p3nrp881272yqzk"

def send_pushover_notification(message):
    try:
        data = {
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "message": message
        }
        response = requests.post("https://api.pushover.net/1/messages.json", data=data)
        print("✅ Pushover sent:", message)
    except Exception as e:
        print("❌ Pushover error:", e)

# ==== Breakout Logic ====
def meets_breakout_conditions(df):
    try:
        macd = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        signal = macd.ewm(span=9).mean()
        crossover = macd.iloc[-2] < signal.iloc[-2] and macd.iloc[-1] > signal.iloc[-1]
        price_spike = df['Volume'].iloc[-1] > 2 * df['Volume'].rolling(window=10).mean().iloc[-1]
        return crossover and price_spike
    except:
        return False

# ==== Screener ====
def check_breakouts(tickers):
    print("📡 Screener is scanning...")
    df_all = yf.download(tickers, period="5d", interval="1d", group_by="ticker", threads=True)

    for ticker in tickers:
        try:
            df = df_all[ticker]
            df["macd_diff"] = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()) - \
                              (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean()
            
            # Force one alert
            if ticker == "QBTS":
                price = df["Close"].iloc[-1]
                message = f"🔥 TEST ALERT: {ticker} @ ${price:.2f}"
                print(message)
                send_pushover_notification(message)
                continue

            if meets_breakout_conditions(df):
                price = df["Close"].iloc[-1]
                message = f"🚀 {ticker} breakout @ ${price:.2f}"
                print(message)
                send_pushover_notification(message)

        except Exception as e:
            print(f"⚠️ Error scanning {ticker}: {e}")

# ==== Full NASDAQ List (Top 50 for now) ====
tickers = [
    "AAPL","MSFT","GOOG","AMZN","NVDA","META","TSLA","AVGO","PEP","ADBE","COST","INTC",
    "CMCSA","NFLX","AMD","QCOM","TXN","INTU","ISRG","AMGN","VRTX","BKNG","GILD","ADP",
    "ADI","MU","REGN","MDLZ","LRCX","PANW","MCHP","CSGP","MAR","CRWD","KLAC","DXCM",
    "PDD","CDNS","FTNT","EXC","SIRI","FAST","ROST","MRVL","EA","WBD","CTAS","MNST",
    "ORLY","PAYX"
]

# ==== Run Screener ====
check_breakouts(tickers)
