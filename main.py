import requests
import time
from collections import defaultdict

BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

CHECK_INTERVAL = 10
WINDOW = 300          # 5 минут
THRESHOLD = 0.3       # 0.3%
ALERT_COOLDOWN = 300  # 5 минут
TOP_INTERVAL = 60

history = defaultdict(list)
last_alert = {}
last_top_report = 0


def send_message(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=10
        )
    except Exception as e:
        print("Ошибка Telegram:", e)


send_message("✅ Крипто-бот запущен")


while True:
    try:
        now = time.time()
        top_growth = []

        for page in range(1, 5):

            response = requests.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": 250,
                    "page": page
                },
                timeout=20
            )

            coins = response.json()

            if not isinstance(coins, list):
                continue

            for coin in coins:

                symbol = coin["symbol"].upper()
                price = coin["current_price"]

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

                    if (
                        symbol not in last_alert
                        or now - last_alert[symbol] > ALERT_COOLDOWN
                    ):

                        send_message(
                            f"🚀 {symbol}\n"
                            f"Рост за 5 минут: +{growth:.2f}%\n"
                            f"Цена: ${price}"
                        )

                        last_alert[symbol] = now

            time.sleep(1)

        if now - last_top_report >= TOP_INTERVAL:

            top_growth.sort(reverse=True)

            msg = "📈 ТОП-10 ЗА 5 МИНУТ\n\n"

            for i, (growth, symbol) in enumerate(top_growth[:10], start=1):
                msg += f"{i}. {symbol} +{growth:.2f}%\n"

            send_message(msg)

            last_top_report = now

        print("Проверка завершена")
        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("Ошибка:", e)
        time.sleep(30)
