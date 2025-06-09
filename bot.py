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


def choose_strategy(performance_file: str = "strategy_performance.csv",
                    default: str = "test_strategy") -> str:
    """Select the strategy with the highest win rate.

    The performance file should contain rows with ``strategy``, ``wins`` and
    ``losses`` columns. If the file does not exist or there is no valid data,
    the provided ``default`` strategy is returned.
    """

    if not os.path.exists(performance_file):
        print(f"Performance file {performance_file} not found. Using default strategy.")
        return default

    best_strategy = default
    best_rate = -1.0

    with open(performance_file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                wins = int(row.get("wins", 0))
                losses = int(row.get("losses", 0))
            except ValueError:
                continue
            total = wins + losses
            if total == 0:
                continue
            rate = wins / total
            if rate > best_rate:
                best_rate = rate
                best_strategy = row.get("strategy", default)

    if best_rate >= 0:
        print(f"Chosen strategy: {best_strategy} (win rate {best_rate:.2%})")
    else:
        print("No valid performance data found. Using default strategy.")

    return best_strategy

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
    strategy = choose_strategy()
    trade_and_log("AAPL", strategy)
