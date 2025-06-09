"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import pandas as pd

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

def simulate_historical_trades(csv_file: str, buy_threshold: float = 500.0) -> None:
    """Simulate a simple buy strategy on historical data and print stats.

    The CSV should contain at least a ``close`` column representing the
    historical closing price of the asset. The function processes each row as
    one candle in time. If the close price is below ``buy_threshold`` a buy is
    simulated for the next candle.
    """

    df = pd.read_csv(csv_file)
    if "close" not in df.columns:
        raise ValueError("CSV must contain a 'close' column")

    total_trades = len(df)
    buy_prices = []
    wins = 0
    highest_after_buy = []

    for i, price in enumerate(df["close"]):
        if price < buy_threshold:
            buy_prices.append(price)
            # Determine if the immediate next candle closes higher
            if i + 1 < len(df) and df["close"].iloc[i + 1] > price:
                wins += 1

            # Highest price seen after the buy point
            if i + 1 < len(df):
                highest_after_buy.append(df["close"].iloc[i + 1 :].max())
            else:
                highest_after_buy.append(price)

    total_buys = len(buy_prices)
    average_entry = sum(buy_prices) / total_buys if total_buys else 0
    win_rate = (wins / total_buys) * 100 if total_buys else 0

    print(f"Total trades processed: {total_trades}")
    print(f"Total simulated buys: {total_buys}")
    print(f"Win rate: {win_rate:.2f}%")
    print(f"Average entry price: {average_entry:.2f}")

    for idx, (entry, high) in enumerate(zip(buy_prices, highest_after_buy), 1):
        potential_gain = ((high - entry) / entry) * 100 if entry else 0
        print(
            f"Buy {idx}: entry {entry:.2f}, highest after buy {high:.2f}, potential gain {potential_gain:.2f}%"
        )

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
