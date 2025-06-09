"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import pandas as pd
import matplotlib.pyplot as plt

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


def simulate_historical_trades(log_file: str = "trade_log.csv") -> None:
    """Visualize historical trades marking skipped trades in a different color."""

    if not os.path.exists(log_file):
        print(f"{log_file} not found.")
        return

    df = pd.read_csv(
        log_file,
        header=None,
        names=["timestamp", "symbol", "price", "action", "strategy"],
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    executed = df[df["action"] != "skipped"]
    skipped = df[df["action"] == "skipped"]

    plt.figure(figsize=(10, 6))
    plt.plot(df["timestamp"], df["price"], label="Price", color="grey", alpha=0.3)

    if not executed.empty:
        plt.scatter(
            executed["timestamp"],
            executed["price"],
            color="green",
            label="Executed",
        )

    if not skipped.empty:
        plt.scatter(
            skipped["timestamp"],
            skipped["price"],
            color="orange",
            label="Skipped",
        )

    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.title("Historical Trades")
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
    simulate_historical_trades()
