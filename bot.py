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


def calculate_atr(api: tradeapi.REST, symbol: str, period: int = 14) -> float | None:
    """Return the average true range for the given symbol."""
    try:
        bars = api.get_bars(symbol, tradeapi.TimeFrame.Day, limit=period + 1).df
    except Exception as e:
        print(f"Failed to fetch bars for {symbol}: {e}")
        return None

    bars = bars.sort_index()
    hl = bars['high'] - bars['low']
    hc = (bars['high'] - bars['close'].shift()).abs()
    lc = (bars['low'] - bars['close'].shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    atr = tr.rolling(period).mean().iloc[-1]
    return float(atr)

def trade_and_log(symbol: str, strategy_used: str = "test_strategy", atr_threshold: float = 1.0):
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

    atr = calculate_atr(api, symbol)
    if atr is None:
        return
    print(f"ATR: {atr:.2f}")

    response = None
    if atr < atr_threshold:
        print(f"ATR below {atr_threshold}. Skipping trade.")
    elif price < 500:  # Placeholder logic
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
            strategy_used,
            atr
        ])

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
