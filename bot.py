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


def simulate_historical_trades(symbol: str, start: str, end: str) -> None:
    """Simulate a simple moving average strategy on historical data and plot results."""
    if not API_KEY or not SECRET_KEY:
        print("Missing Alpaca credentials.")
        return

    api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=BASE_URL)

    try:
        bars = api.get_bars(symbol, tradeapi.rest.TimeFrame.Day, start, end).df
    except Exception as e:
        print(f"Failed to fetch historical data: {e}")
        return

    if bars.empty:
        print("No historical data returned.")
        return

    bars.index = pd.to_datetime(bars.index)
    bars.sort_index(inplace=True)
    bars['SMA50'] = bars['close'].rolling(window=50).mean()

    buy_signals = []
    prev_close = bars['close'].iloc[0]
    prev_sma = bars['SMA50'].iloc[0]
    for idx in range(1, len(bars)):
        close = bars['close'].iloc[idx]
        sma = bars['SMA50'].iloc[idx]
        if pd.notna(prev_sma) and prev_close < prev_sma and close > sma:
            buy_signals.append((bars.index[idx], close))
        prev_close = close
        prev_sma = sma

    plt.figure(figsize=(12, 6))
    plt.plot(bars.index, bars['close'], label='Close Price')
    plt.plot(bars.index, bars['SMA50'], label='50 SMA', linestyle='--')
    if buy_signals:
        dates, prices = zip(*buy_signals)
        plt.scatter(dates, prices, color='green', marker='^', label='Buy Signal')
    plt.title(f'{symbol} Price History with Buy Points')
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
