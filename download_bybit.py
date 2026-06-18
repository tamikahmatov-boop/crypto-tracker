import requests

r = requests.get(
    "https://api.bybit.com/v5/market/instruments-info",
    params={
        "category": "spot",
        "limit": 1000
    },
    timeout=30
).json()

with open("bybit_symbols.txt", "w") as f:

    for coin in r["result"]["list"]:

        symbol = coin["symbol"]

        if symbol.endswith("USDT"):
            f.write(symbol + "\n")

print("Готово")
