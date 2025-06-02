import yfinance as yf
import requests
import pandas as pd

# === PUSHOVER CONFIGURATION ===
PUSHOVER_USER_KEY = "your_user_key_here"
PUSHOVER_API_TOKEN = "your_app_token_here"

def send_pushover_notification(message):
    try:
        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": PUSHOVER_API_TOKEN,
                "user": PUSHOVER_USER_KEY,
                "message": message
            }
        )
        print(f"Pushover response: {response.status_code}")
    except Exception as e:
        print(f"Error sending pushover: {e}")

# === BREAKOUT CHECK LOGIC ===
def meets_breakout_conditions(df):
    if len(df) < 2:
        return False
    close = df["Close"].iloc[-1]
    prev_close = df["Close"].iloc[-2]
    return close > prev_close * 1.03  # breakout if price jumps 3%

def check_breakouts(tickers):
    print("🧠 Screener is scanning...")
    df_all = yf.download(tickers, period="2d", interval="1d", group_by='ticker', threads=True)

    for ticker in tickers:
        try:
            df = df_all[ticker] if len(tickers) > 1 else df_all

            # 🔁 Always trigger test alert for "QBTS"
            if ticker == "QBTS":
                price = df["Close"].iloc[-1]
                message = f"🔥 TEST ALERT: {ticker} at ${price:.2f}"
                print(message)
                send_pushover_notification(message)
                continue

            if meets_breakout_conditions(df):
                price = df["Close"].iloc[-1]
                message = f"{ticker} breakout! Current price: ${price:.2f}"
                print(message)
                send_pushover_notification(message)

        except Exception as e:
            print(f"Error with {ticker}: {e}")

# === MAIN ENTRY POINT ===
if __name__ == "__main__":
    # 🧪 Add or replace tickers here
    tickers = ["QBTS", "TSLA", "AAPL", "AMD", "NVDA"]
    check_breakouts(tickers)
