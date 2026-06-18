import requests
import time
from collections import defaultdict

BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

CHECK_INTERVAL = 10
WINDOW = 300              # 5 минут
THRESHOLD = 0.3           # 0.3%
ALERT_COOLDOWN = 300      # 5 минут
TOP_INTERVAL = 60         # Топ-10 каждую минуту

history = defaultdict(list)
last_alert = {}
last_top_report = 0


def send_message(text):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=10
        )
        print(r.json())
    except Exception as e:
        print("Ошибка Telegram:", e)


send_message("✅ Крипто-бот Bybit запущен")

while True:
    try:
        response = requests.get(
            "https://api.bybit.com/v5/market/tickers",
            params={"category": "spot"},
            timeout=20
        ).json()

        if response.get("retCode") != 0:
            print(response)
            time.sleep(10)
            continue

        now = time.time()
        top_growth = []

        for ticker in response["result"]["list"]:

            symbol = ticker.get("symbol")

            if not symbol or not symbol.endswith("USDT"):
                continue

            try:
                price = float(ticker["lastPrice"])
            except:
                continue

            history[symbol].append((now, price))

            while history[symbol] and now - history[symbol][0][0] > WINDOW:
                history[symbol].pop(0)

            if len(history[symbol]) < 2:
                continue

            old_price = history[symbol][0][1]

            if old_price == 0:
                continue

            growth = (price - old_price) / old_price * 100

            top_growth.append((growth, symbol))

            if growth >= THRESHOLD:

                print(f"Сигнал: {symbol} +{growth:.3f}%")

                if (
                    symbol not in last_alert
                    or now - last_alert[symbol] > ALERT_COOLDOWN
                ):

                    send_message(
                        f"🚀 {symbol}\n"
                        f"📈 Рост за 5 минут: +{growth:.3f}%\n"
                        f"💵 Цена: {price}"
                    )

                    last_alert[symbol] = now

        if now - last_top_report >= TOP_INTERVAL:

            top_growth.sort(reverse=True)

            msg = "📈 ТОП-10 ЗА 5 МИНУТ\n\n"

            for i, (growth, symbol) in enumerate(top_growth[:10], start=1):
                msg += f"{i}. {symbol} +{growth:.2f}%\n"

            send_message(msg)

            last_top_report = now

        print("Проверка завершена")
        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("Ошибка:", e)
        time.sleep(10)
