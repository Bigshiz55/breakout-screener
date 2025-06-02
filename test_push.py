import os
import requests

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
    print(response.status_code, response.text)

send_pushover_notification("✅ Direct test from test_push.py")
