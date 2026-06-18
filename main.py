import requests
import time
from collections import defaultdict

BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

CHECK_INTERVAL = 10
WINDOW = 300
THRESHOLD = 0.3
ALERT_COOLDOWN = 300
TOP_INTERVAL = 60

history = defaultdict(list)
last_alert = {}
last_top_report = 0


def send_message(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=10
        )
    except Exception as e:
        print("Telegram error:", e)


def get_spot_symbols():
    url = "https://api.bybit.com/v5/market/instruments-info"
    r = requests.get(url, params={"category": "spot"}, timeout=20).json()

    symbols = set()

    if "result" in r and "list" in r["result"]:
        for i in r["result"]["list"]:
            if i.get("status") == "Trading":
                symbols.add(i["symbol"])

    return symbols


symbols = get_spot_symbols()

send_message(f"✅ Бот запущен | монет: {len(symbols)}")


while True:
    try:
        now = time.time()

        r = requests.get(
            "https://api.bybit.com/v5/market/tickers",
            params={"category": "spot"},
            timeout=20
        ).json()

        tickers = r.get("result", {}).get("list", [])

        top = []

        for t in tickers:

            symbol = t.get("symbol")
            if symbol not in symbols:
                continue

            try:
                price = float(t.get("lastPrice", 0))
            except:
                continue

            if price <= 0:
                continue

            history[symbol].append((now, price))

            # оставляем 5 минут
            while history[symbol] and now - history[symbol][0][0] > WINDOW:
                history[symbol].pop(0)

            if len(history[symbol]) < 2:
                continue

            old = history[symbol][0][1]
            growth = (price - old) / old * 100

            top.append((growth, symbol))

            print(symbol, round(growth, 3))

            if growth >= THRESHOLD:

                if symbol not in last_alert or now - last_alert[symbol] > ALERT_COOLDOWN:

                    send_message(
                        f"🚀 {symbol}\n"
                        f"Рост 5м: +{growth:.2f}%\n"
                        f"Цена: {price}"
                    )

                    last_alert[symbol] = now

        # ТОП
        if now - last_top_report > TOP_INTERVAL:

            top.sort(reverse=True)

            msg = "📈 ТОП-10 (5 МИН)\n\n"

            for i, (g, s) in enumerate(top[:10], 1):
                msg += f"{i}. {s} +{g:.2f}%\n"

            send_message(msg)

            last_top_report = now

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(10)
