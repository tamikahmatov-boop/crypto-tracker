import requests
import time

BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

WINDOW = 3600
CHECK_INTERVAL = 90
THRESHOLD = 15
ALERT_COOLDOWN = 3600

PAGES = 10

history = {}
last_alert = {}

running = True


# ===== TELEGRAM =====
def send(text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    if reply_markup:
        data["reply_markup"] = reply_markup

    requests.post(url, data=data)


# ===== КНОПКИ =====
def keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "▶️ START", "callback_data": "start"},
                {"text": "⏹ STOP", "callback_data": "stop"}
            ],
            [
                {"text": "📊 STATUS", "callback_data": "status"}
            ]
        ]
    }


# ===== CALLBACK HANDLER =====
def handle_updates():
    global running

    try:
        r = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        ).json()

        for upd in r.get("result", []):

            if "callback_query" in upd:
                data = upd["callback_query"]["data"]

                if data == "start":
                    running = True
                    send("🟢 Бот запущен")

                elif data == "stop":
                    running = False
                    send("🔴 Бот остановлен")

                elif data == "status":
                    send(f"📊 RUNNING: {running}")

    except Exception as e:
        print("update error:", e)


# ===== COINS =====
def get_coins():
    all_coins = []

    for page in range(1, PAGES + 1):
        try:
            r = requests.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": 250,
                    "page": page
                },
                timeout=20
            ).json()

            if isinstance(r, list):
                all_coins.extend(r)

            time.sleep(1)

        except:
            pass

    return all_coins


send("🧪 Бот запущен с кнопками", reply_markup=keyboard())


# ===== MAIN LOOP =====
while True:
    try:
        handle_updates()

        if not running:
            time.sleep(3)
            continue

        now = time.time()

        coins = get_coins()

        for c in coins:

            symbol = c.get("symbol", "").upper()
            price = c.get("current_price")

            if not symbol or not price:
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

            old = history[symbol][0][1]

            growth = (price - old) / old * 100

            print(symbol, growth)

            if growth >= THRESHOLD:

                if symbol not in last_alert or now - last_alert[symbol] > ALERT_COOLDOWN:

                    send(
                        f"🚀 {symbol}\n+{growth:.2f}% за 1 час\n{price}$"
                    )

                    last_alert[symbol] = now

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(5)
