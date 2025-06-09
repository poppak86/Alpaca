"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

from alerts import send_telegram_alert

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

MODE = os.getenv("TRADING_MODE", "paper")  # "live" or "paper"
LOSS_THRESHOLD = int(os.getenv("LOSS_THRESHOLD", "3"))
losses = 0

def switch_mode(new_mode: str, reason: str) -> None:
    """Switch trading mode and send a Telegram alert."""
    global MODE, losses
    if MODE != new_mode:
        MODE = new_mode
        losses = 0
        send_telegram_alert(f"Switched to {MODE.upper()} mode: {reason}")

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
        send_telegram_alert(f"Failed to fetch price for {symbol}: {e}")
        return

    global losses
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
            send_telegram_alert(f"Buy order placed for {symbol} at ${price}")
        except Exception as e:
            print(f"Order failed: {e}")
            send_telegram_alert(f"Order failed for {symbol}: {e}")
            losses += 1
    else:
        print("Price too high. No order placed.")
        send_telegram_alert(f"Skipped trade for {symbol} at ${price}")
        losses += 1

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

    if losses >= LOSS_THRESHOLD and MODE == "live":
        switch_mode("paper", "loss threshold reached")

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
