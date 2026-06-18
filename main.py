
import requests
import time

# =====================
# НАСТРОЙКИ
# =====================

BOT_TOKEN = "ВСТАВЬ_ТОКЕН"
CHAT_ID = "ВСТАВЬ_CHAT_ID"

THRESHOLD = 15.0          # Рост в %
WINDOW = 3600             # 1 час
CHECK_INTERVAL = 30       # Проверка каждые 30 сек
ALERT_COOLDOWN = 3600     # Повторный сигнал через 1 час

# =====================

history = {}
last_alert = {}

# Список монет Bybit
with open("bybit_symbols.txt", "r") as f:
    BYBIT_SYMBOLS = {
        line.strip().upper()
        for line in f
        if line.strip()
    }

print("Монет Bybit:", len(BYBIT_SYMBOLS))


def send_message(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=20
        )
    except Exception as e:
        print("Telegram error:", e)


def get_prices():

    try:

        response = requests.get(
            "https://api.mexc.com/api/v3/ticker/price",
            timeout=20
        )

        data = response.json()

        if not isinstance(data, list):
            return []

        coins = []

        for item in data:

            symbol = item.get("symbol")

            if symbol not in BYBIT_SYMBOLS:
                continue

            try:
                price = float(item["price"])
            except:
                continue

            coins.append({
                "symbol": symbol,
                "price": price
            })

        return coins

    except Exception as e:

        print("MEXC ERROR:", e)

        return []


send_message("🟢 Бот запущен\nСигнал: +15% за 1 час")

while True:

    try:

        now = time.time()

        coins = get_prices()

        for coin in coins:

            symbol = coin["symbol"]
            price = coin["price"]

            if symbol not in history:
                history[symbol] = []

            history[symbol].append((now, price))

            # храним только 1 час
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

                if (
                    symbol not in last_alert
                    or now - last_alert[symbol] > ALERT_COOLDOWN
                ):

                    text = (
                        f"🚀 {symbol}\n\n"
                        f"Рост за 1 час: +{growth:.2f}%\n"
                        f"Цена: {price}"
                    )

                    send_message(text)

                    last_alert[symbol] = now

        time.sleep(CHECK_INTERVAL)

    except Exception as e:

        print("ERROR:", e)

        time.sleep(10)
```
