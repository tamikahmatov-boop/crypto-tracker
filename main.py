import requests
import time

BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

CHECK_INTERVAL = 10
WINDOW = 300               # 5 минут
THRESHOLD = 1              # 1%
ALERT_COOLDOWN = 1800      # 30 минут
TOP_INTERVAL = 60

price_history = {}
last_alert = {}
last_top_report = 0


def send_message(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=10
        )
    except Exception as e:
        print("Telegram error:", e)


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

            symbol = ticker["symbol"]

            if not symbol.endswith("USDT"):
                continue

            try:
                price = float(ticker["lastPrice"])
            except:
                continue

            if symbol not in price_history:
                price_history[symbol] = []

            price_history[symbol].append((now, price))

            # оставляем только последние 5 минут
            price_history[symbol] = [
                x for x in price_history[symbol]
                if now - x[0] <= WINDOW
            ]

            if len(price_history[symbol]) < 2:
                continue

            old_price = price_history[symbol][0][1]

            growth = (price - old_price) / old_price * 100

            top_growth.append((growth, symbol))

            print(symbol, round(growth, 2))

            if growth >= THRESHOLD:

                if (
                    symbol not in last_alert
                    or now - last_alert[symbol] > ALERT_COOLDOWN
                ):

                    send_message(
                        f"🚀 {symbol}\n"
                        f"Рост за 5 минут: +{growth:.2f}%\n"
                        f"Цена: {price}"
                    )

                    last_alert[symbol] = now

        if now - last_top_report > TOP_INTERVAL:

            top_growth.sort(reverse=True)

            msg = "📈 ТОП-10 ЗА 5 МИНУТ\n\n"

            for i, (growth, symbol) in enumerate(top_growth[:10], 1):
                msg += f"{i}. {symbol} +{growth:.2f}%\n"

            send_message(msg)

            last_top_report = now

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("Ошибка:", e)
        time.sleep(10)
