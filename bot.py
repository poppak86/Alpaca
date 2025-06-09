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

# Track last trade time and price per symbol
LAST_TRADES_FILE = "last_trades.json"
LAST_TRADES = {}

if os.path.exists(LAST_TRADES_FILE):
    try:
        with open(LAST_TRADES_FILE, "r") as f:
            LAST_TRADES = json.load(f)
    except Exception:
        LAST_TRADES = {}

def _save_last_trades() -> None:
    """Persist last trade timestamps and prices to file."""
    try:
        with open(LAST_TRADES_FILE, "w") as f:
            json.dump(LAST_TRADES, f)
    except Exception as e:
        print(f"Failed to save last trades: {e}")

def trade_and_log(symbol: str, strategy_used: str = "test_strategy", news_update: bool = False) -> None:
    """Trade any stock and log the decision, price, time, and logic used.

    Parameters
    ----------
    symbol : str
        Ticker symbol to trade.
    strategy_used : str, optional
        Description of strategy for logging purposes.
    news_update : bool, optional
        If True, indicates new sentiment data is available allowing trades even
        within the cooldown window.
    """
    if not API_KEY or not SECRET_KEY:
        print("Missing Alpaca credentials.")
        return

    symbol = symbol.upper()
    api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=BASE_URL)
    print(f"Watching {symbol}...")

    try:
        latest_trade = api.get_latest_trade(symbol)
        price = float(latest_trade.price)
        print(f"Current price: ${price}")
    except Exception as e:
        print(f"Failed to fetch price for {symbol}: {e}")
        return

    # Determine if a recent trade was placed
    skip_trade = False
    last_info = LAST_TRADES.get(symbol)
    if last_info:
        try:
            last_time = datetime.fromisoformat(last_info.get("time"))
            minutes_since = (datetime.utcnow() - last_time).total_seconds() / 60
            last_price = float(last_info.get("price", price))
            drop_pct = (last_price - price) / last_price
            if minutes_since < 15 and not (drop_pct > 0.02 or news_update):
                print(
                    f"Traded {symbol} {minutes_since:.1f} min ago and price hasn't dropped >2%. Skipping buy."
                )
                skip_trade = True
        except Exception:
            pass

    response = None
    if not skip_trade and price < 500:  # Placeholder logic
        try:
            response = api.submit_order(
                symbol=symbol,
                qty=1,
                side="buy",
                type="market",
                time_in_force="gtc",
            )
            print("Buy order placed.")
            LAST_TRADES[symbol] = {
                "time": datetime.utcnow().isoformat(),
                "price": price,
            }
            _save_last_trades()
        except Exception as e:
            print(f"Order failed: {e}")
    elif skip_trade:
        print("Trade skipped due to recent activity.")
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
            bool(news_update)
        ])

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
