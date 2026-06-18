import requests
import time
from collections import defaultdict

BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

THRESHOLD = 1
CHECK_INTERVAL = 30
WINDOW = 300

history = defaultdict(list)
last_alert = {}

def send_message(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=10
        )
    except Exception as e:
        print("Ошибка Telegram:", e)

# Тестовое уведомление
send_message("✅ Крипто-бот Bybit запущен")

while True:
    try:
        response = requests.get(
            "https://api.bybit.com/v5/market/tickers",
            params={"category": "spot"},
            timeout=20
        ).json()

        if response["retCode"] != 0:
            print(response)
            time.sleep(60)
            continue

        tickers = response["result"]["list"]
        now = time.time()

        for ticker in tickers:

            symbol = ticker["symbol"]

            if not symbol.endswith("USDT"):
                continue

            try:
                price = float(ticker["lastPrice"])
            except:
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

            if growth >= THRESHOLD:

                if (
                    symbol not in last_alert
                    or now - last_alert[symbol] > WINDOW
                ):

                    send_message(
                        f"🚀 {symbol}\n"
                        f"Рост за 1 час: {growth:.2f}%\n"
                        f"Цена: {price}"
                    )

                    last_alert[symbol] = now

        print("Проверка выполнена")
        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("Ошибка:", e)
        time.sleep(60)
