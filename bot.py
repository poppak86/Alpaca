"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import pandas as pd
from colorama import Fore, Style, init
import sys

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


def simulate_historical_trades(filename: str = "trade_log.csv", spike_threshold: float = 0.05) -> None:
    """Print the trade log highlighting skipped trades that later spiked in price."""
    init(autoreset=True)

    if not os.path.exists(filename):
        print(f"{filename} not found.")
        return

    df = pd.read_csv(
        filename,
        header=None,
        names=["timestamp", "symbol", "price", "action", "strategy"],
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    for idx, row in df.iterrows():
        output = f"{row.timestamp} {row.symbol} ${row.price:.2f} {row.action} {row.strategy}"
        if row.action == "skipped":
            later = df[(df.symbol == row.symbol) & (df.timestamp > row.timestamp)]
            if not later.empty and later.price.max() >= row.price * (1 + spike_threshold):
                output = f"{Fore.RED}{output}{Style.RESET_ALL}"
        print(output)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "simulate":
        simulate_historical_trades()
    else:
        trade_and_log("AAPL", "price_under_500")
