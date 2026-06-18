import requests
import time

BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

CHECK_INTERVAL = 10
WINDOW = 300
THRESHOLD = 0.3
ALERT_COOLDOWN = 300

history = {}
last_alert = {}


def send_message(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=10
        )
    except Exception as e:
        print("Telegram error:", e)


send_message("🧪 REST бот запущен")


while True:
    try:
        now = time.time()

        resp = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            timeout=20
        )

        data = resp.json()

        # 🔥 ВАЖНО: защита от ошибки API
        if not isinstance(data, list):
            print("API ERROR:", data)
            time.sleep(5)
            continue

        for item in data:

            if not isinstance(item, dict):
                continue

            symbol = item.get("symbol")
            price = item.get("price")

            if not symbol or not price:
                continue

            if not symbol.endswith("USDT"):
                continue

            try:
                price = float(price)
            except:
                continue

            if symbol not in history:
                history[symbol] = []

            history[symbol].append((now, price))

            # чистим 5 минут
            history[symbol] = [
                x for x in history[symbol]
                if now - x[0] <= WINDOW
            ]

            if len(history[symbol]) < 2:
                continue

            old = history[symbol][0][1]

            if old <= 0:
                continue

            growth = (price - old) / old * 100

            print(symbol, growth)

            if growth >= THRESHOLD:

                if symbol not in last_alert or now - last_alert[symbol] > ALERT_COOLDOWN:

                    send_message(
                        f"🚀 {symbol}\n"
                        f"Рост 5м: +{growth:.2f}%\n"
                        f"Цена: {price}"
                    )

                    last_alert[symbol] = now

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(5)
