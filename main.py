import os
import time
import requests

BOT_TOKEN = os.getenv("8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw")
CHAT_ID = os.getenv("6716942872")

THRESHOLD = 10  # рост в %
CHECK_INTERVAL = 60  # 1 минута
last_alert = {}


def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=10
    )


send_message("✅ Крипто-бот запущен")

while True:
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 250,
                "page": 1,
                "price_change_percentage": "1h"
            },
            timeout=20
        )

        coins = response.json()

        for coin in coins:

            symbol = coin["symbol"].upper()

            growth = coin.get("price_change_percentage_1h_in_currency")

            price = coin.get("current_price")

            if growth is None:
                continue

            if growth >= THRESHOLD:

                now = time.time()

                if symbol not in last_alert or now - last_alert[symbol] > 3600:

                    send_message(
                        f"🚀 {symbol}\n"
                        f"Рост за 1 час: {growth:.2f}%\n"
                        f"Цена: ${price}"
                    )

                    last_alert[symbol] = now

        print("Проверка выполнена")

    except Exception as e:
        print("Ошибка:", e)

    time.sleep(CHECK_INTERVAL)
