import requests
import os
import time
import yfinance as yf
from ta.trend import MACD

def send_pushover_notification(message):
    user_key = os.getenv("PUSHOVER_USER_KEY")
    app_token = os.getenv("PUSHOVER_APP_TOKEN")

    if not user_key or not app_token:
        print("Missing Pushover credentials")
        return

    data = {
        "token": app_token,
        "user": user_key,
        "message": message,
    }

    response = requests.post("https://api.pushover.net/1/messages.json", data=data)
    if response.status_code != 200:
        print(f"Error sending notification: {response.text}")
    else:
        print("✅ Notification sent!")

def check_breakouts(tickers):
    print("📈 Screener is running...")
    df = yf.download(tickers, period="1d", interval="1m", group_by='ticker', threads=True)

    for ticker in tickers:
        try:
            data = df[ticker] if isinstance(df.columns, pd.MultiIndex) else df
            close = data['Close'].dropna()
            if close.empty:
                continue

            macd = MACD(close=close)
            data['macd_diff'] = macd.macd_diff().squeeze()
            last_value = data['macd_diff'].iloc[-1]

            if last_value > 0:
                price = close.iloc[-1]
                send_pushover_notification(f"{ticker} breakout! Price: ${price:.2f}")

        except Exception as e:
            print(f"Error with {ticker}: {e}")

TICKERS_TO_WATCH = ["QBTS", "FAAS", "BBAI"]
INTERVAL_SECONDS = 60

while True:
    check_breakouts(TICKERS_TO_WATCH)
    time.sleep(INTERVAL_SECONDS)
