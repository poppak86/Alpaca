"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
import json
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from datetime import timedelta

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"


def save_backtest_result(strategy: str, symbol: str, win_rate: float, trade_count: int) -> None:
    """Append backtest results to backtest_results.json."""
    result = {
        "strategy": strategy,
        "symbol": symbol,
        "win_rate": win_rate,
        "trade_count": trade_count,
    }

    try:
        with open("backtest_results.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    if not isinstance(data, list):
        data = []

    data.append(result)

    with open("backtest_results.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

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


def backtest_strategy(symbol: str, strategy_name: str = "test_strategy") -> None:
    """Very simple backtest placeholder using historical daily bars."""
    if not API_KEY or not SECRET_KEY:
        print("Missing Alpaca credentials for backtest.")
        return

    api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=BASE_URL)

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    try:
        bars = api.get_bars(symbol, tradeapi.TimeFrame.Day, start=start_date.isoformat(), end=end_date.isoformat(), limit=10)
    except Exception as e:
        print(f"Failed to get historical data for {symbol}: {e}")
        return

    wins = 0
    trades = 0

    for bar in bars:
        close_price = float(bar.c)
        open_price = float(bar.o)

        if close_price < 500:  # same logic as trade_and_log
            trades += 1
            if close_price > open_price:
                wins += 1

    win_rate = wins / trades if trades else 0

    print(f"Backtest result for {strategy_name} on {symbol}: {win_rate * 100:.2f}% win rate over {trades} trades")

    save_backtest_result(strategy_name, symbol, win_rate, trades)

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
    backtest_strategy("AAPL", "price_under_500")
