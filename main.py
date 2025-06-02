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
        requests.post("https://api.pushover.net/1/messages.json", data=payload)
        print(f"✅ Pushover sent: {title}")
    except Exception as e:
        print(f"❌ Pushover failed: {e}")

# === BREAKOUT SCANNER ===
def check_breakouts(ticker_list, label=""):
    for symbol in ticker_list:
        try:
            data = yf.download(symbol, period="5d", interval="5m", progress=False, threads=False)
            if data.empty or len(data) < 50:
                print(f"{label}{symbol}: ❌ No valid price data.")
                continue

            close = data["Close"]
            exp1 = close.ewm(span=12, adjust=False).mean()
            exp2 = close.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            macd_cross = macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]

            typical_price = (data["High"] + data["Low"] + data["Close"]) / 3
            vwap = (typical_price * data["Volume"]).cumsum() / data["Volume"].cumsum()
            vwap_reclaim = close.iloc[-1] > vwap.iloc[-1]

            avg_volume = data["Volume"].iloc[-20:-1].mean()
            last_volume = data["Volume"].iloc[-1]
            volume_spike = last_volume > 1.5 * avg_volume

            print(f"{label}{symbol}: MACD={macd_cross}, VWAP={vwap_reclaim}, VOL Spike={volume_spike}")

            if macd_cross and vwap_reclaim and volume_spike:
                message = f"{symbol} breakout!\nMACD: ✅\nVWAP: ✅\nVolume Spike: ✅"
                send_pushover_notification(f"{label}Breakout: {symbol}", message)

        except Exception as e:
            print(f"{label}{symbol} error: {e}")

# === FULL NASDAQ TICKERS (300+ cleaned and filtered) ===
tickers = [
    "AAPL", "MSFT", "GOOG", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "AVGO", "PEP", "ADBE", "COST", "INTC", "CMCSA",
    "NFLX", "AMD", "QCOM", "TXN", "INTU", "ISRG", "AMGN", "VRTX", "BKNG", "GILD", "ADP", "ADI", "MU", "REGN", "MDLZ",
    "LRCX", "PANW", "MCHP", "CSGP", "MAR", "CRWD", "KLAC", "DXCM", "PDD", "CDNS", "FTNT", "EXC", "SIRI", "FAST",
    "ROST", "MRVL", "EA", "WBD", "CTAS", "MNST", "ORLY", "PAYX", "ZM", "DOCU", "TEAM", "SNOW", "DDOG", "BILL", "ROKU",
    "SHOP", "SE", "ABNB", "MDB", "CRSP", "PLTR", "ZS", "SPLK", "OKTA", "NTNX", "NET", "FSLY", "U", "UPST", "COIN",
    "SOFI", "LCID", "RIVN", "FUBO", "CVNA", "OSTK", "MTCH", "TTD", "DKNG", "SQ", "PYPL", "PINS", "SNAP", "RBLX",
    "ETSY", "TWLO", "DASH", "SEDG", "ENPH", "RUN", "NIO", "XPEV", "LI", "BIDU", "JD", "BABA", "NTES", "GS", "JPM",
    "BAC", "C", "WFC", "USB", "SCHW", "COF", "TROW", "NDAQ", "V", "MA", "AXP", "SPGI", "MSCI", "ICE", "CME", "MCO",
    "BRO", "AJG", "PGR", "TRV", "ALL", "CB", "MKTX", "EVR", "SF", "RJF", "BEN", "IVZ", "TFC", "FITB", "KEY", "HBAN",
    "RF", "ZION", "CFG", "MTB", "CMA", "ALLY", "WAL", "NYCB", "FRC", "PACW", "WDC", "STX", "NTAP", "BNTX", "MRNA",
    "ILMN", "EXAS", "SRPT", "IONS", "ACAD", "BMRN", "PTCT", "BIIB", "NBIX", "ALNY", "SGEN", "INCY", "KRTX", "TXG",
    "NVCR", "IDXX", "SWAV", "PEN", "GMED", "AORT", "BSX", "BSGM", "XENT", "MASI", "TNDM", "SILK", "CSII", "ICUI",
    "INSP", "EW", "NVRO", "XRAY", "RGEN", "RMD", "OMCL", "SYK", "BDX", "ZBH", "ALGN", "TFX", "HRC", "COO", "STE",
    "PODD", "TMO", "PKI", "A", "QDEL", "BIO", "IQV", "DGX", "LH", "MTD", "WAT", "BRKR", "CRL", "NEOG", "ABC", "MCK", "CAH"
]

# === REVERSE SPLIT WATCH LIST ===
reverse_split_tickers = ["APDN", "BNRG", "TAOP", "EKSO"]

# === MAIN LOOP ===
print("✅ Screener started...")

while True:
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n🔄 Scan running at {now}")
    send_pushover_notification("✅ Screener Check-In", f"Heartbeat at {now}")
    check_breakouts(tickers)
    check_breakouts(reverse_split_tickers, label="RS: ")
    time.sleep(60)
