import requests
import time
from collections import defaultdict

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

CHECK_INTERVAL = 10      # Проверка каждые 10 секунд
WINDOW = 300             # Анализ за 5 минут
THRESHOLD = 1            # Сигнал при росте от 1%
ALERT_COOLDOWN = 1800    # Повтор сигнала по монете через 30 минут
TOP_REPORT_INTERVAL = 60 # Топ-10 каждую минуту

history = defaultdict(list)
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
        print("Ошибка Telegram:", e)


def get_icon(growth):
    if growth >= 10:
        return "💎"
    elif growth >= 5:
        return "🔥"
    elif growth >= 3:
        return "🚀"
    else:
        return "🟢"


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

        tickers = response["result"]["list"]
        now = time.time()

        top_growth = []

        for ticker in tickers:

            symbol = ticker.get("symbol")

            if not symbol or not symbol.endswith("USDT"):
                continue

            try:
                price = float(ticker["lastPrice"])
            except:
                continue

            if price <= 0:
                continue

            history[symbol].append((now, price))

            # Храним только последние 5 минут
            while history[symbol] and now - history[symbol][0][0] > WINDOW:
                history[symbol].pop(0)

            if len(history[symbol]) < 2:
                continue

            old_price = history[symbol][0][1]

            if old_price <= 0:
                continue

            growth = (price - old_price) / old_price * 100

            top_growth.append((growth, symbol))

            # Уведомление по отдельной монете
            if growth >= THRESHOLD:

                if (
                    symbol not in last_alert
                    or now - last_alert[symbol] > ALERT_COOLDOWN
                ):

                    icon = get_icon(growth)

                    send_message(
                        f"{icon} {symbol}\n\n"
                        f"📈 Рост: +{growth:.2f}%\n"
                        f"💵 Цена: {price}\n"
                        f"⏱ За последние 5 минут"
                    )

                    last_alert[symbol] = now

        # Топ-10 за 5 минут
        if now - last_top_report >= TOP_REPORT_INTERVAL:

            top_growth.sort(reverse=True)

            message = "📈 ТОП-10 ЗА 5 МИНУТ\n\n"

            for i, (growth, symbol) in enumerate(top_growth[:10], start=1):
                message += (
                    f"{i}. {symbol}  +{growth:.2f}%\n"
                )

            send_message(message)

            last_top_report = now

        print("Проверка завершена")
        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("Ошибка:", e)
        time.sleep(10)
