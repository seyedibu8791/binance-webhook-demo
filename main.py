from flask import Flask, request, jsonify
from binance.client import Client
import os

app = Flask(__name__)

API_KEY = os.environ.get("BINANCE_API_KEY")
API_SECRET = os.environ.get("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET, testnet=True)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    symbol = data['symbol'].replace("BINANCE:", "")
    action = data['action']
    leverage = int(data.get("leverage", 10))
    trade_size_type = data.get("trade_size_type", "Percent")
    trade_amount = float(data.get("trade_amount", 0.1))

    try:
        client.futures_change_leverage(symbol=symbol, leverage=leverage)
    except Exception as e:
        return jsonify({"status":"error","message":str(e)})

    if trade_size_type == "Percent":
        balance = float(client.futures_account_balance()[0]['balance'])
        qty = round(balance * trade_amount / 100, 3)
    else:
        qty = trade_amount

    try:
        if action == "BUY":
            client.futures_create_order(symbol=symbol, side="BUY", type="MARKET", quantity=qty)
        elif action == "SELL":
            client.futures_create_order(symbol=symbol, side="SELL", type="MARKET", quantity=qty)
        elif action == "EXIT_LONG":
            client.futures_create_order(symbol=symbol, side="SELL", type="MARKET", quantity=qty)
        elif action == "EXIT_SHORT":
            client.futures_create_order(symbol=symbol, side="BUY", type="MARKET", quantity=qty)
    except Exception as e:
        return jsonify({"status":"error","message":str(e)})

    return jsonify({"status":"success","data":data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
