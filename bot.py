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

# Directory and helper for storing AI brain memory outputs
MEMORY_DIR = "memory"


def _append_to_memory(brain: str, text: str) -> None:
    """Append a line of text to the memory file for the given brain."""
    os.makedirs(MEMORY_DIR, exist_ok=True)
    path = os.path.join(MEMORY_DIR, f"{brain}_memory.txt")
    with open(path, "a") as mem_file:
        mem_file.write(f"{datetime.utcnow().isoformat()} - {text}\n")


def analyst_brain(symbol: str, price: float) -> str:
    """Basic analysis step for the given symbol."""
    output = f"Analyzed {symbol} at price {price}"
    _append_to_memory("analyst", output)
    return output


def strategist_brain(price: float) -> str:
    """Decide whether to buy based on price."""
    decision = "buy" if price < 500 else "skip"
    _append_to_memory("strategist", f"Decision {decision} for price {price}")
    return decision


def news_brain(symbol: str) -> str:
    """Placeholder for news processing."""
    output = f"No news processing implemented for {symbol}"
    _append_to_memory("news", output)
    return output


def risk_brain(symbol: str, price: float) -> str:
    """Placeholder for risk checks."""
    output = f"Risk check for {symbol} at {price} not implemented"
    _append_to_memory("risk", output)
    return output

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
        analyst_brain(symbol, price)
    except Exception as e:
        print(f"Failed to fetch price for {symbol}: {e}")
        _append_to_memory("analyst", f"Failed analysis for {symbol}: {e}")
        return

    response = None
    decision = strategist_brain(price)
    if decision == "buy":
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

    news_brain(symbol)
    risk_brain(symbol, price)

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
