"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame

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

def download_historical_data(symbol: str, start: str, end: str):
    """Return daily price bars for the given date range."""
    if not API_KEY or not SECRET_KEY:
        print("Missing Alpaca credentials.")
        return []

    api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=BASE_URL)
    try:
        bars = api.get_bars(symbol, TimeFrame.Day, start=start, end=end)
        return list(bars)
    except Exception as e:
        print(f"Failed to download historical data: {e}")
        return []


def simulate_historical_trades(symbol: str, start: str, end: str) -> List[Dict[str, str]]:
    """Simulate the price_under_500 strategy over historical bars."""
    history = download_historical_data(symbol, start, end)
    trades = []
    for bar in history:
        price = float(bar.c)
        action = "buy" if price < 500 else "skip"
        timestamp = bar.t.isoformat() if hasattr(bar.t, "isoformat") else str(bar.t)
        trades.append({"time": timestamp, "price": price, "action": action})
    return trades

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
    # Example historical simulation
    # history = simulate_historical_trades("AAPL", "2023-01-01", "2023-01-31")
    # print(history)
