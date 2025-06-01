import requests
import os

print("Breakout screener is running")

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
        print("Notification sent!")

# Trigger a test notification
send_pushover_notification("Breakout Screener is now LIVE!")
