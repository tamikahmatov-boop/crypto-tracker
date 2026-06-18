import requests
import time

# ===== ТВОИ ДАННЫЕ =====
BOT_TOKEN = "ВСТАВЬ_ТОКЕН"
CHAT_ID = "ВСТАВЬ_CHAT_ID"

WINDOW = 300
CHECK_INTERVAL = 10
THRESHOLD = 0.3
ALERT_COOLDOWN = 300

history = {}
last_alert = {}


# ===== TELEGRAM =====
def send(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=10
        )
    except Exception as e:
        print("Telegram error:", e)


send("🧪 Bybit бот запущен (FIX версия)")


# ===== ПОЛУЧЕНИЕ ДАННЫХ BYBIT =====
def get_prices():
    try:
        r = requests.get(
            "https://api.bybit.com/v5/market/tickers",
            params={"category": "spot"},
            timeout=20
        )

        data = r.json()

        # 🔥 защита от кривого ответа
        if not isinstance(data, dict):
            print("BAD RESPONSE (not dict)")
            return []

        result = data.get("result")
        if not isinstance(result, dict):
            return []

        lst = result.get("list")
        if not isinstance(lst, list):
            return []

        return lst

    except Exception as e:
        print("API ERROR:", e)
        return []


# ===== ОСНОВНОЙ ЦИКЛ =====
while True:
    try:
        now = time.time()

        tickers = get_prices()

        for t in tickers:

            if not isinstance(t, dict):
                continue

            symbol = t.get("symbol")
            price = t.get("lastPrice")

            if not symbol or not price:
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

            print(symbol, round(growth, 3))

            if growth >= THRESHOLD:

                if symbol not in last_alert or now - last_alert[symbol] > ALERT_COOLDOWN:

                    send(
                        f"🚀 {symbol}\n"
                        f"Рост 5м: +{growth:.2f}%\n"
                        f"Цена: {price}"
                    )

                    last_alert[symbol] = now

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(5)
