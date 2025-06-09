"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
import json
from typing import Dict
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

STRATEGY_PRIORITY_FILE = "strategy_priorities.json"


def save_strategy_priorities(priorities: Dict[str, float], file_path: str = STRATEGY_PRIORITY_FILE) -> None:
    """Persist strategy priority scores to a JSON file."""
    with open(file_path, "w") as f:
        json.dump(priorities, f, indent=2)


def load_strategy_priorities(file_path: str = STRATEGY_PRIORITY_FILE) -> Dict[str, float]:
    """Load strategy priority scores if they exist."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}


STRATEGY_PRIORITIES = load_strategy_priorities()

def trade_and_log(symbol: str, strategy_used: str = "test_strategy"):
    """Trade any stock and log the decision, price, time, and logic used."""
    if not API_KEY or not SECRET_KEY:
        print("Missing Alpaca credentials.")
        return

    api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=BASE_URL)
    priority = STRATEGY_PRIORITIES.get(strategy_used, 0)
    print(f"Watching {symbol.upper()} using '{strategy_used}' (priority {priority})...")

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
