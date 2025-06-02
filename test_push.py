import requests

PUSHOVER_USER_KEY = "your_user_key_here"
PUSHOVER_API_TOKEN = "your_api_token_here"

def send_pushover_notification(title, message):
    print(f"Sending Pushover alert: {title} — {message}")
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": title,
        "message": message
    }
    try:
        response = requests.post(url, data=data)
        print(f"Pushover response code: {response.status_code}")
        print(f"Pushover response text: {response.text}")
    except Exception as e:
        print(f"Pushover error: {e}")

send_pushover_notification("🚨
