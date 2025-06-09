"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

def analyze_trade_log():
    """Analyze the trade_log.csv file and print a summary per strategy."""
    log_file = "trade_log.csv"
    if not os.path.exists(log_file):
        print("trade_log.csv not found.")
        return

    strategies = {}
    with open(log_file, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 5:
                continue
            _, _symbol, price, action, strategy = row
            price = float(price)
            info = strategies.setdefault(
                strategy, {"total": 0, "executed": 0, "skipped": 0, "prices": []}
            )
            info["total"] += 1
            if action == "buy":
                info["executed"] += 1
                info["prices"].append(price)
            else:
                info["skipped"] += 1

    for strategy, data in strategies.items():
        avg_price = (
            sum(data["prices"]) / len(data["prices"]) if data["prices"] else 0
        )
        print(f"Strategy: {strategy}")
        print(f"- Trades: {data['total']}")
        print(f"- Executed: {data['executed']}")
        print(f"- Skipped: {data['skipped']}")
        print(f"- Avg Buy Price: ${avg_price:.2f}")


def trade_and_log(symbol: str, strategy_used: str = "test_strategy"):
    """Trade any stock and log the decision, price, time, and logic used."""
    if not API_KEY or not SECRET_KEY:
        print("Missing Alpaca credentials.")
        return

    api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=BASE_URL)
    print(f"Watching {symbol.upper()}...")

    try:
        latest_trade = api.get_latest_trade(symbol)
        price = float(latest_trade.price)
        print(f"Current price: ${price}")
    except Exception as e:
        print(f"Failed to fetch price for {symbol}: {e}")
        return

    response = None
    if price < 500:  # Placeholder logic
        try:
            response = api.submit_order(
                symbol=symbol,
                qty=1,
                side="buy",
                type="market",
                time_in_force="gtc",
            )
            print("Buy order placed.")
        except Exception as e:
            print(f"Order failed: {e}")
    else:
        print("Price too high. No order placed.")

    # Log everything for future learning
    with open("trade_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            symbol,
            price,
            "buy" if response else "skipped",
            strategy_used
        ])

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
