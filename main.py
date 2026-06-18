import os
import time
import requests
from collections import defaultdict

BOT_TOKEN = os.getenv("8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw")
CHAT_ID = os.getenv("6716942872")

history = defaultdict(list)
last_alert = {}

while True:
    try:
        data = requests.get(
            "https://api.binance.com/api/v3/ticker/price"
        ).json()

        now = time.time()

        for coin in data:

            symbol = coin["symbol"]

            if not symbol.endswith("USDT"):
                continue

            price = float(coin["price"])

            history[symbol].append((now, price))

            history[symbol] = [
                x for x in history[symbol]
                if now - x[0] <= 3600
            ]

            if len(history[symbol]) < 2:
                continue

            old_price = history[symbol][0][1]

            if old_price == 0:
                continue

            growth = (price - old_price) / old_price * 100

            if growth >= 10:

                if symbol not in last_alert or now - last_alert[symbol] > 3600:

                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        data={
                            "chat_id": CHAT_ID,
                            "text":
                            f"🚀 {symbol}\n"
                            f"Рост за час: {growth:.2f}%\n"
                            f"Цена: {price}"
                        }
                    )

                    last_alert[symbol] = now

        time.sleep(60)

    except Exception as e:
        print(e)
        time.sleep(60)
