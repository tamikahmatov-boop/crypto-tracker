import websocket
import json
import time
import requests
from collections import defaultdict

BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

THRESHOLD = 0.1  # временно очень низкий для теста
WINDOW = 300

history = defaultdict(list)


def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text}
    )


send_message("🧪 Бот запущен (тест рынка)")


def process(symbol, price):
    now = time.time()

    history[symbol].append((now, price))

    history[symbol] = [
        x for x in history[symbol]
        if now - x[0] <= WINDOW
    ]

    if len(history[symbol]) < 2:
        return

    old = history[symbol][0][1]
    growth = (price - old) / old * 100

    print(symbol, growth)

    if growth >= THRESHOLD:
        send_message(f"🚀 {symbol}\n+{growth:.2f}%\n{price}")


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


while True:
    try:
        ws = websocket.WebSocketApp(
            "wss://stream.binance.com:9443/ws",
            on_message=on_message,
            on_open=on_open
        )
        ws.run_forever()

    except Exception as e:
        print("ERROR:", e)
        time.sleep(5)
