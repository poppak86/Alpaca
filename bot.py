"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from typing import List, Dict

from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import pandas as pd
import yfinance as yf

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


def simulate_historical_trades(symbol: str, price_threshold: float, days: int = 60) -> Dict[str, float]:
    """Backtest a simple threshold strategy using Yahoo Finance data."""
    data = yf.download(symbol, period=f"{days}d", interval="1d", progress=False)
    if data.empty or len(data) < 2:
        return {"threshold": price_threshold, "win_rate": 0.0, "trades": 0}
    if isinstance(data.columns, pd.MultiIndex):
        data = data.xs(symbol, level=1, axis=1)

    wins = 0
    trades = 0
    closes = data["Close"].tolist()
    opens = data["Open"].tolist()

    for i in range(len(data) - 1):
        if closes[i] < price_threshold:
            entry = opens[i + 1]
            exit_price = closes[i + 1]
            trades += 1
            if exit_price > entry:
                wins += 1

    win_rate = wins / trades if trades else 0.0
    return {"threshold": price_threshold, "win_rate": round(win_rate, 2), "trades": trades}


def compare_strategies(symbol: str, thresholds: List[float]) -> List[Dict[str, float]]:
    """Simulate several strategies and print a comparison table."""
    results = [simulate_historical_trades(symbol, t) for t in thresholds]
    print(f"Results for {symbol}:")
    print("Threshold  Win Rate  Trades")
    for res in results:
        print(f"{res['threshold']:>9}  {res['win_rate']:.2f}      {res['trades']}")
    return results

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
