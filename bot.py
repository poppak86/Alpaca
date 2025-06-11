"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import requests

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message: str) -> None:
    """Send a Telegram message if credentials are available."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    except Exception as exc:
        print(f"Failed to send Telegram message: {exc}")

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
    action = "skipped"
    if price < 500:  # Placeholder logic
        try:
            response = api.submit_order(
                symbol=symbol,
                qty=1,
                side="buy",
                type="market",
                time_in_force="gtc",
            )
            action = "buy"
            print("Buy order placed.")
        except Exception as e:
            print(f"Order failed: {e}")
    else:
        print("Price too high. No order placed.")

    last_price = None
    if os.path.exists("trade_log.csv"):
        with open("trade_log.csv") as f:
            rows = list(csv.reader(f))
            for row in reversed(rows):
                if len(row) >= 3 and row[1] == symbol:
                    try:
                        last_price = float(row[2])
                        break
                    except ValueError:
                        pass

    profit_loss = price - last_price if last_price is not None else 0.0

    # Log everything for future learning
    with open("trade_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            symbol,
            price,
            action,
            strategy_used,
            profit_loss,
        ])

    if response:
        msg = (
            f"{symbol} {action} at ${price:.2f}. "
            f"Strategy: {strategy_used}. P/L: ${profit_loss:.2f}"
        )
        send_telegram(msg)

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
