"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
import random
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"


def get_strategy_performance(strategy: str) -> float:
    """Return a simple performance metric for the given strategy."""
    if not os.path.exists("trade_log.csv"):
        return 0.5
    with open("trade_log.csv", newline="") as f:
        rows = [r for r in csv.reader(f) if len(r) >= 5 and r[4] == strategy]
    if not rows:
        return 0.5
    buys = sum(1 for r in rows if r[3] == "buy")
    return buys / len(rows)


def get_recent_win_rate(lookback: int = 20) -> float:
    """Calculate a naive win rate from recent trades."""
    if not os.path.exists("trade_log.csv"):
        return 0.5
    with open("trade_log.csv", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        return 0.5
    recent = rows[-lookback:]
    wins = sum(1 for r in recent if len(r) >= 4 and r[3] == "buy")
    return wins / len(recent)


def compute_trade_score(symbol: str, strategy_used: str) -> int:
    """Score the trade from 0-100 using sentiment, strategy performance, and win rate."""
    sentiment = random.random()
    strategy_perf = get_strategy_performance(strategy_used)
    win_rate = get_recent_win_rate()
    score = int(100 * (0.4 * sentiment + 0.3 * strategy_perf + 0.3 * win_rate))
    return score

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
    action = "buy" if response else "skipped"
    score = compute_trade_score(symbol, strategy_used)
    print(f"Trade score: {score}")
    with open("trade_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            symbol,
            price,
            action,
            strategy_used,
            score
        ])

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
