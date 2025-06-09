"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
import json
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"


def update_strategy_scores(strategy: str, win: bool) -> None:
    """Update or create persistent win rate stats for a strategy."""
    try:
        with open("strategy_scores.json", "r") as f:
            scores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        scores = {}

    if strategy not in scores:
        scores[strategy] = {"wins": 0, "trades": 0, "win_rate": 0.0}

    scores[strategy]["trades"] += 1
    if win:
        scores[strategy]["wins"] += 1

    wins = scores[strategy]["wins"]
    trades = scores[strategy]["trades"]
    scores[strategy]["win_rate"] = round(wins / trades, 4) if trades else 0

    with open("strategy_scores.json", "w") as f:
        json.dump(scores, f, indent=2)

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
    win = False
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

            # Very naive win check based on immediate price change
            try:
                new_price = float(api.get_latest_trade(symbol).price)
                win = new_price > price
            except Exception:
                win = False
        except Exception as e:
            print(f"Order failed: {e}")
    else:
        print("Price too high. No order placed.")

    # Log everything for future learning
    log_exists = os.path.isfile("trade_log.csv")
    with open("trade_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not log_exists:
            writer.writerow(["timestamp", "symbol", "price", "action", "strategy", "win"])
        writer.writerow([
            datetime.utcnow().isoformat(),
            symbol,
            price,
            "buy" if response else "skipped",
            strategy_used,
            int(win)
        ])

    update_strategy_scores(strategy_used, win)

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
