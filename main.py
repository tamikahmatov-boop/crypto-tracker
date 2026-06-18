import requests
import time

BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

WINDOW = 3600
CHECK_INTERVAL = 60
THRESHOLD = 15
PAGES = 10

history = {}
running = True

message_id = None
offset = 0


# ===== TELEGRAM =====
def send(text, markup=None):
    global message_id

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    if markup:
        data["reply_markup"] = markup

    r = requests.post(url, data=data).json()

    message_id = r["result"]["message_id"]


def edit(text, markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"

    data = {
        "chat_id": CHAT_ID,
        "message_id": message_id,
        "text": text
    }

    if markup:
        data["reply_markup"] = markup

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
                {"text": "📊 STATUS", "callback_data": "status"},
                {"text": "🔥 TOP", "callback_data": "top"}
            ]
        ]
    }


# ===== CALLBACK =====
def handle_updates():
    global running, offset

    r = requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
        params={"offset": offset + 1}
    ).json()

    for upd in r.get("result", []):

        offset = upd["update_id"]

        if "callback_query" not in upd:
            continue

        data = upd["callback_query"]["data"]

        if data == "start":
            running = True

        elif data == "stop":
            running = False

        elif data == "status":
            pass

        elif data == "top":
            pass


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

            time.sleep(0.5)

        except:
            pass

    return all_coins


# ===== INIT =====
send("🧪 LIVE DASHBOARD запущен", keyboard())


# ===== LOOP =====
while True:
    try:
        handle_updates()

        if not running:
            edit("⏸ БОТ ОСТАНОВЛЕН", keyboard())
            time.sleep(3)
            continue

        now = time.time()
        coins = get_coins()

        total_pumps = 0

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

            if old <= 0:
                continue

            growth = (price - old) / old * 100

            if growth >= THRESHOLD:
                total_pumps += 1

        text = (
            "📊 LIVE DASHBOARD\n\n"
            f"🔥 Pump coins: {total_pumps}\n"
            f"⏱ Interval: {CHECK_INTERVAL}s\n"
            f"📈 Threshold: {THRESHOLD}%\n"
            f"▶️ Running: {running}"
        )

        edit(text, keyboard())

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(5)
