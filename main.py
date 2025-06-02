import os
import time
import requests
import yfinance as yf
import pandas as pd
from ta.trend import MACD

# === FULL NASDAQ TICKER LIST ===
tickers = ["AACB","AACBR","AACBU","AACG","AACIU","AADR","AAL","AAME","AAOI","AAON","AAPB","AAPD","AAPG","AAPL","AAPU","AARD","AAVM","AAXJ","ABAT","ABCL","ABCS","ABEO","ABIG","ABL","ABLLL","ABLLW","ABLV","ABLVW","ABNB","ABOS","ABP","ABPWW","ABSI","ABTS","ABUS","ABVC","ABVE","ABVEW","ABVX","ACAD","ACB","ACDC","ACET","ACGL","ACGLN","ACGLO","ACHC","ACHV","ACIC","ACIU","ACIW","ACLS","ACLX","ACMR","ACNB","ACNT","ACOG","ACON","ACONW","ACRS","ACRV","ACT","ACTG","ACTU","ACWI","ACWX","ACXP","ADAG","ADAP","ADBE","ADBG","ADD","ADEA","ADGM","ADI","ADIL","ADMA","ADN","ADNWW","ADP","ADPT","ADSE","ADSEW","ADSK","ADTN","ADTX","ADUR","ADUS","ADV","ADVB","ADVM","ADVWW","ADXN","AEHL","AEHR","AEI","AEIS","AEMD","AENT","AENTW","AEP","AERT","AERTW","AEVA","AEVAW","AEYE","AFBI","AFCG","AFJK","AFJKR","AFJKU","AFRI","AFRIW","AFRM","AFSC","AFYA","AGAE","AGEM","AGEN","AGFY","AGGA","AGH","AGIO","AGIX","AGMH","AGMI","AGNC","AGNCL","AGNCM","AGNCN","AGNCO","AGNCP","AGNG","AGRI","AGYS","AGZD","AHCO","AHG","AIA","AIFE","AIFER","AIFEU","AIFF","AIFU","AIHS","AIMD","AIMDW","AIOT","AIP","AIPI","AIQ","AIRE","AIRG","AIRJ","AIRJW","AIRL","AIRR","AIRS","AIRT","AIRTP","AISP","AISPW","AIXI","AKAM","AKAN","AKBA","AKRO","AKTX","AKYA","ALAB","ALAR","ALBT","ALCO","ALCY","ALCYU","ALCYW","ALDF","ALDFU","ALDFW","ALDX","ALEC","ALF","ALFUU","ALFUW","ALGM","ALGN","ALGS","ALGT","ALHC","ALIL","ALKS","ALKT","ALLO","ALLR","ALLT","ALLW","ALMS","ALMU","ALNT","ALNY","ALOT","ALRM","ALRS","ALT","ALTI","ALTO","ALTS","ALTY","ALVO","ALVOW","ALXO","ALZN","AMAL","AMAT","AMBA","AMBR","AMCX","AMD","AMDD","AMDG","AMDL","AMDS","AMED","AMGN","AMID","AMIX","AMKR","AMLX","AMOD","AMODW","AMPG","AMPGW","AMPH","AMPL","AMRK","AMRN","AMRX","AMSC","AMSF","AMST","AMTX","AMUU","AMWD","AMZD","AMZN","AMZU","AMZZ","ANAB","ANDE","ANEB","ANGH","ANGHW","ANGI","ANGL","ANGO","ANIK","ANIP","ANIX","ANL","ANNA","ANNAW","ANNX","ANSC","ANSCU","ANSCW","ANSS","ANTA","ANTE","ANTX","ANY","AOHY","AOSL","AOTG","AOUT","APA","APDN","APED","APEI","APGE","API","APLD","APLM","APLMW","APLS","APLT","APM","APOG","APP","APPF","APPN","APPS","APPX","APRE","APVO","APWC","APYX","AQB","AQMS","AQST","AQWA","ARAI","ARAY","ARBB","ARBE","ARBEW","ARBK","ARBKL","ARCB","ARCC","ARCT","ARDX","AREB","AREBW","AREC","ARGX","ARHS","ARKO","ARKOW","ARKR","ARLP","ARM","ARMG","AROW","ARQ","ARQQ","ARQQW","ARQT","ARRY","ARTL","ARTNA","ARTV","ARTW","ARVN","ARVR","ARWR","ASBP","ASBPW","ASET","ASLE","ASMB","ASMG","ASML","ASND","ASNS","ASO","ASPC","ASPCR","ASPCU","ASPI","ASPS","ASPSW","ASPSZ","ASRT","ASRV","ASST","ASTC","ASTE","ASTH","ASTI","ASTL","ASTLW","ASTS","ASUR","ASYS","ATAI","ATAT","ATCOL","ATEC","ATER","ATEX","ATGL","ATHA","ATHE","ATHR","ATII","ATIIU","ATIIW","ATLC","ATLCL","ATLCP","ATLCZ","ATLN","ATLO","ATLX","ATMC","ATMCR","ATMCU","ATMCW","ATMV","ATMVR","ATMVU","ATNF","ATNFW","ATNI","ATOM","ATOS","ATPC","ATRA","ATRC","ATRO","ATXG","ATXS","ATYR","AUBN","AUDC","AUID","AUMI","AUPH","AUR","AURA","AUROW","AUTL","AUUD","AUUDW","AVAH","AVAV","AVBP","AVDL","AVDX","AVGB","AVGG","AVGO","AVGX"]

# === PUSHOVER NOTIFICATION ===
def send_pushover_notification(message):
    user_key = os.getenv("PUSHOVER_USER_KEY")
    app_token = os.getenv("PUSHOVER_APP_TOKEN")
    if not user_key or not app_token:
        print("❌ Missing Pushover credentials")
        return
    data = {
        "token": app_token,
        "user": user_key,
        "message": message,
    }
    response = requests.post("https://api.pushover.net/1/messages.json", data=data)
    if response.status_code != 200:
        print(f"❌ Error sending notification: {response.text}")
    else:
        print("✅ Notification sent!")

# === BREAKOUT CONDITION CHECK ===
def meets_breakout_conditions(df):
    if len(df) < 35:
        return False
    macd = MACD(df["Close"])
    df["macd_diff"] = macd.macd_diff().squeeze()
    recent_vol = df["Volume"].iloc[-1]
    avg_vol = df["Volume"].rolling(window=20).mean().iloc[-2]
    vol_spike = recent_vol > avg_vol * 1.5
    macd_crossover = df["macd_diff"].iloc[-1] > 0 and df["macd_diff"].iloc[-2] <= 0
    vwap_reclaim = df["Close"].iloc[-1] > df["Close"].mean()
    return vol_spike and macd_crossover and vwap_reclaim

# === MAIN SCANNER ===
def check_breakouts(tickers):
    print("📡 Screener scanning...")
    df_all = yf.download(tickers, period="1d", interval="1m", group_by="ticker", progress=False)
    for ticker in tickers:
        try:
            df = df_all[ticker]
            if meets_breakout_conditions(df):
                price = df["Close"].iloc[-1]
                message = f"🚨 {ticker} breakout! Price: ${price:.2f}"
                print(message)
                send_pushover_notification(message)
        except Exception as e:
            print(f"⚠️ Error with {ticker}: {e}")

# === START LOOP ===
if __name__ == "__main__":
    print("🚀 Breakout screener is LIVE")
    while True:
        check_breakouts(tickers)
        time.sleep(60)
