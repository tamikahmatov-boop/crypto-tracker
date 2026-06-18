import websocket
import json

def on_message(ws, message):
    data = json.loads(message)

    if "data" in data:
        for item in data["data"][:5]:
            print(item["s"], item["c"])

def on_open(ws):
    print("CONNECTED TO MARKET")

    ws.send(json.dumps({
        "method": "SUBSCRIBE",
        "params": ["!ticker@arr"],
        "id": 1
    }))

ws = websocket.WebSocketApp(
    "wss://stream.binance.com:9443/ws",
    on_message=on_message,
    on_open=on_open
)

ws.run_forever()
