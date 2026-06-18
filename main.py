import requests
import time

BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

print("START")

r = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={"chat_id": CHAT_ID, "text": "🧪 ТЕСТ РАБОТАЕТ"}
)

print(r.text)

while True:
    time.sleep(10)
