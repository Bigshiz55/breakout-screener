def check_breakouts(tickers):
    print("🧠 Screener is scanning...")
    df_all = yf.download(tickers, period="1d", interval="1m", group_by="ticker", progress=False)
    for ticker in tickers:
        try:
            df = df_all[ticker]
            
            # 🔁 TEMPORARY TEST OVERRIDE
            if ticker == "QBTS":  # Force alert for this stock
                price = df["Close"].iloc[-1]
                message = f"🔥 TEST ALERT: {ticker} forced breakout! Price: ${price:.2f}"
                print(message)
                send_pushover_notification(message)
                continue

            if meets_breakout_conditions(df):
                price = df["Close"].iloc[-1]
                message = f"{ticker} breakout! Price: ${price:.2f}"
                print(message)
                send_pushover_notification(message)
        except Exception as e:
            print(f"Error with {ticker}: {e}")
