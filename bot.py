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


def smart_position_sizing(symbol: str, price: float, api: tradeapi.REST) -> int:
    """Determine share quantity based on past win rate for the given symbol."""
    history = []

    if os.path.exists("trade_log.csv"):
        with open("trade_log.csv", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 6 and row[1] == symbol:
                    result = row[5]
                    try:
                        # Treat numeric result as profit/loss amount
                        profit = float(result)
                        history.append(1 if profit > 0 else 0)
                    except ValueError:
                        # Or categorical win/loss strings
                        history.append(1 if result.lower() == "win" else 0)

    win_rate = sum(history) / len(history) if history else 0.5

    base_qty = 1
    qty = int(base_qty * (0.5 + 1.5 * win_rate))
    qty = max(1, qty)

    try:
        cash = float(api.get_account().cash)
        max_affordable = int(cash // price)
        qty = min(qty, max_affordable)
    except Exception:
        pass

    return qty

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
    qty = smart_position_sizing(symbol, price, api)
    if price < 500 and qty > 0:  # Placeholder logic
        try:
            response = api.submit_order(
                symbol=symbol,
                qty=qty,
                side="buy",
                type="market",
                time_in_force="gtc",
            )
            print(f"Buy order placed for {qty} shares.")
        except Exception as e:
            print(f"Order failed: {e}")
    else:
        print("Price too high. No order placed.")

    # Log everything for future learning
    file_exists = os.path.exists("trade_log.csv")
    with open("trade_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "symbol", "price", "action", "strategy", "qty"])
        writer.writerow([
            datetime.utcnow().isoformat(),
            symbol,
            price,
            "buy" if response else "skipped",
            strategy_used,
            qty if response else 0
        ])

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
