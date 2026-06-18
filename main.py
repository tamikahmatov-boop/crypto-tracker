with open("bybit_symbols.txt", "r") as f:
    BYBIT_SYMBOLS = set(
        line.strip().upper()
        for line in f
        if line.strip()
    )

print("BYBIT монет загружено:", len(BYBIT_SYMBOLS))
import requests

def get_prices():

    try:

        response = requests.get(
            "https://api.mexc.com/api/v3/ticker/price",
            timeout=20
        )

        data = response.json()

        if not isinstance(data, list):
            print("API ERROR:", data)
            return []

        coins = []

        for item in data:

            symbol = item.get("symbol")

            if not symbol:
                continue

            # только монеты, которые есть в списке Bybit
            if symbol not in BYBIT_SYMBOLS:
                continue

            try:
                price = float(item["price"])
            except:
                continue

            coins.append({
                "symbol": symbol,
                "price": price
            })

        return coins

    except Exception as e:

        print("MEXC ERROR:", e)

        return []
