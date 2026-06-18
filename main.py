import os
import time
import requests
from collections import defaultdict

BOT_TOKEN = os.getenv("8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw")
CHAT_ID = os.getenv("6716942872")

CHECK_INTERVAL = 60
THRESHOLD = 10
WINDOW = 3600

history = defaultdict(list)
last_alert = {}

def send_message(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=10
        )
    except Exception as e:
        print("Ошибка Telegram:", e)

# Тестовое уведомление при запуске
send_message("✅ Крипто-бот запущен и работает")

while True:
    try:
        response = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            timeout=10
        )

        tickers = response.json()
        now = time.time()

        top_growth = []

        for ticker in tickers:

            symbol = ticker["symbol"]

            if not symbol.endswith("USDT"):
                continue

            try:
                price = float(ticker["price"])
            except:
                continue

            if price <= 0:
                continue

            history[symbol].append((now, price))

            while history[symbol] and now - history[symbol][0][0] > WINDOW:
                history[symbol].pop(0)

            if len(history[symbol]) < 2:
                continue

            old_price = history[symbol][0][1]

            if old_price <= 0:
                continue

            growth = (price - old_price) / old_price * 100

            top_growth.append((growth, symbol))

            if growth >= THRESHOLD:

                if symbol not in last_alert or now - last_alert[symbol] > WINDOW:

                    message = (
                        f"🚀 {symbol}\n"
                        f"Рост за 1 час: {growth:.2f}%\n"
                        f"Цена: {price}"
                    )

                    send_message(message)

                    last_alert[symbol] = now

        top_growth.sort(reverse=True)

        print("\n===== ТОП-5 ЗА ЧАС =====")

        for growth, symbol in top_growth[:5]:
            print(f"{symbol}: {growth:.2f}%")

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("Ошибка:", e)
        time.sleep(60)
