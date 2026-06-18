import websocket
import json
import time
import threading
import requests
from collections import defaultdict

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

THRESHOLD = 0.3
WINDOW = 300
ALERT_COOLDOWN = 300

price_history = defaultdict(list)
last_alert = {}


# ===== TELEGRAM =====
def send_message(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=10
        )
    except Exception as e:
        print("Telegram error:", e)


# ===== ОБРАБОТКА ЦЕН =====
def process(symbol, price):

    now = time.time()

    price_history[symbol].append((now, price))

    # оставляем последние 5 минут
    price_history[symbol] = [
        x for x in price_history[symbol]
        if now - x[0] <= WINDOW
    ]

    if len(price_history[symbol]) < 2:
        return

    old = price_history[symbol][0][1]
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


# ===== WEBSOCKET =====
def on_message(ws, message):
    data = json.loads(message)

    if "data" not in data:
        return

    for item in data["data"]:
        symbol = item["s"]
        price = float(item["c"])
        process(symbol, price)


def on_open(ws):
    print("CONNECTED")

    ws.send(json.dumps({
        "method": "SUBSCRIBE",
        "params": ["!ticker@arr"],
        "id": 1
    }))

    # ===== ТЕСТОВОЕ УВЕДОМЛЕНИЕ =====
    send_message(
        "🧪 ТЕСТ УВЕДОМЛЕНИЯ\n\n"
        "✅ Telegram подключён\n"
        "🚀 Бот успешно запущен"
    )


def run():
    while True:
        try:
            ws = websocket.WebSocketApp(
                "wss://stream.binance.com:9443/ws",
                on_message=on_message,
                on_open=on_open
            )

            ws.run_forever()

        except Exception as e:
            print("WS error:", e)
            time.sleep(5)


run()
