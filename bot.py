"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
import json
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

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

def evolve_strategy(trade_log_path: str = "trade_log.csv", priorities_path: str = "strategy_priority.json") -> None:
    """Analyze trade history and raise priority for winning strategies."""
    if not os.path.exists(trade_log_path):
        print("Trade log not found.")
        return

    # Load existing priorities
    if os.path.exists(priorities_path):
        try:
            with open(priorities_path) as f:
                priorities = json.load(f)
        except Exception:
            priorities = {}
    else:
        priorities = {}

    stats: dict[str, dict[str, int]] = {}
    with open(trade_log_path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 5:
                continue
            strategy = row[4]
            result = row[3].lower()
            if strategy not in stats:
                stats[strategy] = {"wins": 0, "total": 0}
            stats[strategy]["total"] += 1
            if result == "win":
                stats[strategy]["wins"] += 1

    for strategy, s in stats.items():
        if s["total"] == 0:
            continue
        win_rate = s["wins"] / s["total"]
        if win_rate > 0.7:
            priorities[strategy] = priorities.get(strategy, 0) + 1

    with open(priorities_path, "w") as f:
        json.dump(priorities, f, indent=2)

    for strategy, value in priorities.items():
        print(f"Strategy '{strategy}' priority: {value}")

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
