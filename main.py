import requests
import time
from collections import defaultdict

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

CHECK_INTERVAL = 10
WINDOW = 300              # 5 минут
THRESHOLD = 0.3           # 0.3%
ALERT_COOLDOWN = 300      # 5 минут
TOP_INTERVAL = 60         # топ каждые 60 сек

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


# ===== ПОЛУЧАЕМ ВСЕ SPOT МОНЕТЫ BYBIT =====
def get_symbols():
    url = "https://api.bybit.com/v5/market/instruments-info"
    params = {"category": "spot"}

    data = requests.get(url, params=params, timeout=20).json()

    symbols = []
    for item in data["result"]["list"]:
        if item["status"] == "Trading":
            symbols.append(item["symbol"])

    return symbols


symbols_list = get_symbols()

send_message(f"✅ Bybit бот запущен\nМонет: {len(symbols_list)}")


while True:
    try:
        now = time.time()
        top_growth = []

        # ===== ПОЛУЧАЕМ ЦЕНЫ ВСЕХ МОНЕТ =====
        response = requests.get(
            "https://api.bybit.com/v5/market/tickers",
            params={"category": "spot"},
            timeout=20
        ).json()

        tickers = response["result"]["list"]

        for t in tickers:

            symbol = t.get("symbol")
            if symbol not in symbols_list:
                continue

            try:
                price = float(t["lastPrice"])
            except:
                continue

            history[symbol].append((now, price))

            # держим только 5 минут
            while history[symbol] and now - history[symbol][0][0] > WINDOW:
                history[symbol].pop(0)

            if len(history[symbol]) < 2:
                continue

            old_price = history[symbol][0][1]

            if old_price <= 0:
                continue

            growth = (price - old_price) / old_price * 100

            top_growth.append((growth, symbol))

            # ===== СИГНАЛЫ =====
            if growth >= THRESHOLD:

                if symbol not in last_alert or now - last_alert[symbol] > ALERT_COOLDOWN:

                    send_message(
                        f"🚀 {symbol}\n"
                        f"Рост за 5 минут: +{growth:.2f}%\n"
                        f"Цена: {price}"
                    )

                    last_alert[symbol] = now

        # ===== ТОП =====
        if now - last_top_report >= TOP_INTERVAL:

            top_growth.sort(reverse=True)

            msg = "📈 ТОП-10 BYBIT (5 МИН)\n\n"

            for i, (g, s) in enumerate(top_growth[:10], 1):
                msg += f"{i}. {s} +{g:.2f}%\n"

            send_message(msg)

            last_top_report = now

        print("OK")
        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("Ошибка:", e)
        time.sleep(10)
