import requests
import time

BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

CHECK_INTERVAL = 10
WINDOW = 300          # 5 минут
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


send_message("🧪 REST бот запущен (без WebSocket)")


while True:
    try:
        now = time.time()

        r = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            timeout=20
        ).json()

        for item in r:

            symbol = item["symbol"]

            if not symbol.endswith("USDT"):
                continue

            try:
                price = float(item["price"])
            except:
                continue

            if symbol not in history:
                history[symbol] = []

            history[symbol].append((now, price))

            # чистим старое (5 минут)
            history[symbol] = [
                x for x in history[symbol]
                if now - x[0] <= WINDOW
            ]

            if len(history[symbol]) < 2:
                continue

            old = history[symbol][0][1]

            growth = (price - old) / old * 100

            print(symbol, round(growth, 3))

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
