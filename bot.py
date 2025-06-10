"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"


def calculate_atr(api: tradeapi.REST, symbol: str, window: int = 14) -> float | None:
    """Return a simple ATR using high-low ranges."""
    try:
        bars = api.get_bars(symbol, TimeFrame.Day, limit=window)
        df = bars.df if hasattr(bars, "df") else None
        if df is None or df.empty:
            return None
        return float((df["high"] - df["low"]).abs().mean())
    except Exception as e:
        print(f"Failed to calculate ATR for {symbol}: {e}")
        return None

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

    atr = calculate_atr(api, symbol)
    stop_price = round(price * 0.99, 2)
    take_price = round(price * 1.02, 2)
    if atr:
        stop_price = round(price - atr, 2)
        take_price = round(price + atr, 2)

    response = None
    if price < 500:  # Placeholder logic
        try:
            response = api.submit_order(
                symbol=symbol,
                qty=1,
                side="buy",
                type="market",
                time_in_force="gtc",
                order_class="bracket",
                stop_loss={"stop_price": stop_price},
                take_profit={"limit_price": take_price},
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
            stop_price,
            take_price,
            atr if atr else "n/a",
        ])

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
