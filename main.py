import requests
import time

BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

WINDOW = 3600
CHECK_INTERVAL = 90
THRESHOLD = 15
ALERT_COOLDOWN = 3600

PAGES = 10

MIN_PRICE = 0.0001
MIN_MARKET_CAP = 10_000_000

IGNORE = {
    "USDT",
    "USDC",
    "BUSD",
    "DAI",
    "FDUSD",
    "TUSD",
    "USDE",
    "USDD"
}

history = {}
last_alert = {}

dashboard_message_id = None


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


def send_dashboard(text):
    global dashboard_message_id

    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=20
        ).json()

        if r.get("ok"):
            dashboard_message_id = r["result"]["message_id"]

    except Exception as e:
        print("Dashboard send error:", e)


def edit_dashboard(text):
    global dashboard_message_id

    if dashboard_message_id is None:
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
            data={
                "chat_id": CHAT_ID,
                "message_id": dashboard_message_id,
                "text": text
            },
            timeout=20
        )

    except:
        pass


def get_coins():
    coins = []

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
                timeout=30
            )

            data = r.json()

            if isinstance(data, list):
                coins.extend(data)

            time.sleep(1)

        except Exception as e:
            print("CoinGecko error:", e)

    return coins


send_message("🟢 Бот запущен")

send_dashboard("📊 Загрузка рынка...")

while True:

    try:

        now = time.time()

        coins = get_coins()

        pumps = 0

        for coin in coins:

            symbol = coin.get("symbol", "").upper()
            price = coin.get("current_price")
            market_cap = coin.get("market_cap", 0)

            if not symbol:
                continue

            if symbol in IGNORE:
                continue

            if not price:
                continue

            if price < MIN_PRICE:
                continue

            if market_cap < MIN_MARKET_CAP:
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

                    send_message(
                        f"🚀 {symbol}\n"
                        f"Рост за 1 час: +{growth:.2f}%\n"
                        f"Цена: ${price:,.8f}"
                    )

                    last_alert[symbol] = now

        dashboard = (
            "📊 LIVE DASHBOARD\n\n"
            f"🪙 Монет: {len(coins)}\n"
            f"🚀 Пампов >15%: {pumps}\n"
            f"⏱ Интервал: {CHECK_INTERVAL} сек\n"
            f"📈 Порог: {THRESHOLD}%\n"
            f"🕒 Окно анализа: 1 час"
        )

        edit_dashboard(dashboard)

        time.sleep(CHECK_INTERVAL)

    except Exception as e:

        print("ERROR:", e)

        time.sleep(10)
