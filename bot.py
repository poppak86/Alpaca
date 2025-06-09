"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

# URLs for live and paper trading
LIVE_BASE_URL = "https://api.alpaca.markets"
PAPER_BASE_URL = "https://paper-api.alpaca.markets"


class ModeManager:
    """Handles switching between live and paper trading modes."""

    def __init__(self, cooldown_hours: int = 1):
        self.mode = "live"
        self.failed_trades = 0
        self.profitable_trades = 0
        self.cooldown_start = None
        self.cooldown_duration = timedelta(hours=cooldown_hours)

    def log_transition(self, new_mode: str, reason: str) -> None:
        """Append a mode change event to mode_log.csv."""
        with open("mode_log.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.utcnow().isoformat(), new_mode, reason])
        print(f"MODE -> {new_mode} ({reason})")

    def base_url(self) -> str:
        return LIVE_BASE_URL if self.mode == "live" else PAPER_BASE_URL

    def record_trade(self, success: bool) -> None:
        """Update counters and switch modes if needed."""
        now = datetime.utcnow()

        if self.mode == "live":
            if not success:
                self.failed_trades += 1
                if self.failed_trades >= 3:
                    self.mode = "paper"
                    self.log_transition("paper", "3 consecutive failed live trades")
                    self.cooldown_start = now
                    self.failed_trades = 0
        else:  # paper mode
            if success:
                self.profitable_trades += 1

            if self.cooldown_start and now - self.cooldown_start >= self.cooldown_duration:
                if self.profitable_trades >= 2:
                    self.mode = "live"
                    self.log_transition("live", "paper trading success")
                    self.cooldown_start = None
                else:
                    self.log_transition("paper", "cooldown extended due to insufficient success")
                    self.cooldown_start = now
                self.profitable_trades = 0

def trade_and_log(symbol: str, strategy_used: str = "test_strategy", base_url: str = PAPER_BASE_URL) -> bool:
    """Trade any stock and log the decision, price, time, and logic used.

    Returns True if a trade was executed, False otherwise.
    """
    if not API_KEY or not SECRET_KEY:
        print("Missing Alpaca credentials.")
        return False

    api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=base_url)
    print(f"Watching {symbol.upper()}...")

    try:
        latest_trade = api.get_latest_trade(symbol)
        price = float(latest_trade.price)
        print(f"Current price: ${price}")
    except Exception as e:
        print(f"Failed to fetch price for {symbol}: {e}")
        return False

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
            response = None
    else:
        print("Price too high. No order placed.")
        response = None

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
    return response is not None

if __name__ == "__main__":
    manager = ModeManager()
    symbol = "AAPL"
    while True:
        success = trade_and_log(symbol, "price_under_500", base_url=manager.base_url())
        manager.record_trade(success)
        time.sleep(60)
