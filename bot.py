"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from dataclasses import dataclass
import random
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

@dataclass
class PriceUnderStrategy:
    """Simple strategy that buys when the price is below a threshold."""
    threshold: float

    def __call__(self, price: float) -> bool:
        return price < self.threshold


def mutate_strategy(strategy: PriceUnderStrategy, change: float = 0.02) -> PriceUnderStrategy:
    """Return a new strategy with its threshold slightly mutated.

    Args:
        strategy: The strategy instance to mutate.
        change: Maximum percentage change to apply (e.g. 0.02 is ±2%).
    """
    delta = strategy.threshold * change * random.uniform(-1, 1)
    new_threshold = strategy.threshold + delta
    return PriceUnderStrategy(threshold=new_threshold)

def trade_and_log(symbol: str, strategy: PriceUnderStrategy):
    """Trade any stock using the given strategy and log the decision."""
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
    if strategy(price):
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
            f"price_under_{strategy.threshold:.2f}"
        ])

if __name__ == "__main__":
    base = PriceUnderStrategy(500)
    test_strategy = mutate_strategy(base)
    trade_and_log("AAPL", test_strategy)
