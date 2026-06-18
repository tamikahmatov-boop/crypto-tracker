import requests
import time

BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

THRESHOLD = 15          # рост в %
WINDOW = 3600           # 1 час
CHECK_INTERVAL = 60     # проверка раз в минуту
ALERT_COOLDOWN = 3600   # повторное уведомление через час

history = {}
last_alert = {}


def send(text):
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
        print("Telegram error:", e)


send("🟢 MEXC бот запущен")


while True:
    try:
        now = time.time()

        r = requests.get(
            "https://api.mexc.com/api/v3/ticker/price",
            timeout=20
        )

        data = r.json()

        if not isinstance(data, list):
            print(data)
            time.sleep(10)
            continue

        pumps = 0

        for coin in data:

            symbol = coin.get("symbol")

            if not symbol or not symbol.endswith("USDT"):
                continue

            try:
                price = float(coin["price"])
            except:
                continue

            if symbol not in history:
                history[symbol] = []

            history[symbol].append((now, price))

            history[symbol] = [
                x for x in history[symbol]
                if now - x[0] <= WINDOW
            ]

            if len(history[symbol]) < 2:
                continue

            old_price = history[symbol][0][1]

            if old_price <= 0:
                continue

            growth = (price - old_price) / old_price * 100

            if growth >= THRESHOLD:

                pumps += 1

                if (
                    symbol not in last_alert
                    or now - last_alert[symbol] > ALERT_COOLDOWN
                ):

                    send(
                        f"🚀 {symbol}\n"
                        f"Рост за 1 час: +{growth:.2f}%\n"
                        f"Цена: {price}"
                    )

                    last_alert[symbol] = now

        print("Pumps:", pumps)

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(10)
