import json
from flask import Flask, request
import requests

# ============================
# CONFIG (EDIT THESE)
# ============================

API_KEY = "YOUR-LIVE-CAPITAL-API-KEY"     # <-- paste your REAL Capital.com API key here
ACCOUNT_TYPE = "live"                      # "live" or "demo"

CAPITAL_BASE = "https://api-capital.backend-capital.com"

# TradingView sends: "CAPITALCOM:XAUUSD"
# Capital.com EPIC: "XAUUSD"
EPIC_MAPPING = {
    "CAPITALCOM:XAUUSD": "XAUUSD",
    "XAUUSD": "XAUUSD"
}

# Your 6 SAFE strategy IDs
ALLOWED_STRATEGIES = [
    "fib0382_bear",
    "fib0382_bull",
    "fib05_bull",
    "fib05_bear",
    "fib0618_bull",
    "fib0618_bear"
]

# Lot size for each strategy (edit if needed)
QTY = {
    "fib0382_bear": 1,
    "fib0382_bull": 1,
    "fib05_bull": 1,
    "fib05_bear": 1,
    "fib0618_bull": 1,
    "fib0618_bear": 1
}

# ============================
# FLASK APP
# ============================

app = Flask(__name__)

def place_market_order(direction, epic, size):
    """Send a market order to Capital.com"""
    endpoint = f"{CAPITAL_BASE}/v1/positions"

    headers = {
        "X-CAP-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "direction": direction.upper(),   # BUY or SELL
        "epic": epic,
        "size": size,
        "orderType": "MARKET"
    }

    response = requests.post(endpoint, headers=headers, json=payload)
    print("Capital.com Response:", response.status_code, response.text)
    return response.status_code == 200


@app.route("/webhook", methods=["POST"])
def webhook():
    """Receive webhook alerts from Webhook.site (forwarded from TradingView)."""
    try:
        data = request.json
        print("Received Alert:", data)

        strategy_id = data.get("strategy")
        signal = data.get("signal")
        tv_symbol = data.get("symbol")

        # Check strategy
        if strategy_id not in ALLOWED_STRATEGIES:
            print(f"Ignored: Unknown strategy '{strategy_id}'")
            return "ignored"

        # Check symbol
        if tv_symbol not in EPIC_MAPPING:
            print(f"Ignored: Unknown symbol '{tv_symbol}'")
            return "ignored"

        epic = EPIC_MAPPING[tv_symbol]
        size = QTY[strategy_id]

        # BUY or SELL
        if signal == "buy":
            print(f"Executing BUY from {strategy_id}")
            place_market_order("BUY", epic, size)

        elif signal == "sell":
            print(f"Executing SELL from {strategy_id}")
            place_market_order("SELL", epic, size)

        else:
            print("Unknown signal:", signal)

        return "ok"

    except Exception as e:
        print("ERROR:", e)
        return "error", 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
