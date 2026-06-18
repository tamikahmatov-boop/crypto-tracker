import requests
import time
from collections import defaultdict

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8626739818:AAFt7kmdfTgTVlXD-5FnKOVYq1fvNW9hUAw"
CHAT_ID = "6716942872"

CHECK_INTERVAL = 60      # проверка каждую минуту
WINDOW = 3600            # 1 час
THRESHOLD = 15           # +15%
ALERT_COOLDOWN = 3600    # 1 час
TOP_INTERVAL = 3600      # топ-10 раз в час

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
        print("Telegram error:", e)


# ===== ТЕСТ =====
send_message("✅ Крипто-бот запущен (15% за 1 час)")


while True:
    try:
        now = time.time()
        top_growth = []

        # ===== 4 страницы = ~1000 монет =====
        for page in range(1, 5):

            response = requests.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": 250,
                    "page": page
                },
                timeout=20
            )

            coins = response.json()

            if not isinstance(coins, list):
                print("CoinGecko error:", coins)
                continue

            for coin in coins:

                symbol = coin.get("symbol", "").upper()
                price = coin.get("current_price")

                if not price:
                    continue

                history[symbol].append((now, price))

                # оставляем только 1 час
                while history[symbol] and now - history[symbol][0][0] > WINDOW:
                    history[symbol].pop(0)

                if len(history[symbol]) < 2:
                    continue

                old_price = history[symbol][0][1]

                if old_price <= 0:
                    continue

                growth = (price - old_price) / old_price * 100

                top_growth.append((growth, symbol))

                # ===== СИГНАЛ =====
                if growth >= THRESHOLD:

                    if (
                        symbol not in last_alert
                        or now - last_alert[symbol] > ALERT_COOLDOWN
                    ):

                        send_message(
                            f"🚀 {symbol}\n"
                            f"Рост за 1 час: +{growth:.2f}%\n"
                            f"Цена: ${price}"
                        )

                        last_alert[symbol] = now

            time.sleep(1)  # защита от лимитов API

        # ===== ТОП-10 =====
        if now - last_top_report >= TOP_INTERVAL:

            top_growth.sort(reverse=True)

            msg = "📈 ТОП-10 ЗА 1 ЧАС\n\n"

            for i, (growth, symbol) in enumerate(top_growth[:10], start=1):
                msg += f"{i}. {symbol} +{growth:.2f}%\n"

            send_message(msg)

            last_top_report = now

        print("Проверка завершена")
        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("Ошибка:", e)
        time.sleep(30)
