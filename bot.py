"""Self-learning AI trading bot starter using Alpaca.

This simplified example now tracks each strategy's win rate and profit/loss.
If a strategy falls below a 40% win rate after 10 trades it is marked inactive
and a Telegram notification is sent if credentials are provided.
"""

import os
import csv
import time
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import requests

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(message: str) -> None:
    """Send a message via Telegram if credentials are available."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = (
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        f"?chat_id={TELEGRAM_CHAT_ID}&text={message}"
    )
    try:
        requests.get(url, timeout=10)
    except Exception as exc:
        print(f"Failed to send Telegram message: {exc}")


def update_strategy_stats(strategy: str, profit: float) -> None:
    """Update win rate and P/L for the given strategy."""
    stats_file = "strategy_stats.csv"
    data = {}

    # Load existing stats
    if os.path.exists(stats_file):
        with open(stats_file, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data[row["strategy"]] = row

    # Initialize strategy if not present
    if strategy not in data:
        data[strategy] = {
            "strategy": strategy,
            "wins": "0",
            "total_trades": "0",
            "total_profit": "0.0",
            "active": "True",
        }

    entry = data[strategy]
    wins = int(entry["wins"])
    total_trades = int(entry["total_trades"])
    total_profit = float(entry["total_profit"])
    active = entry.get("active", "True") == "True"

    if profit > 0:
        wins += 1
    total_trades += 1
    total_profit += profit

    win_rate = wins / total_trades if total_trades else 0

    # Check deactivation condition
    if active and total_trades >= 10 and win_rate < 0.4:
        active = False
        send_telegram_message(
            f"Strategy {strategy} deactivated: win rate {win_rate:.0%} over {total_trades} trades"
        )

    data[strategy] = {
        "strategy": strategy,
        "wins": str(wins),
        "total_trades": str(total_trades),
        "total_profit": f"{total_profit}",
        "active": str(active),
    }

    # Write updated stats
    with open(stats_file, "w", newline="") as f:
        fieldnames = ["strategy", "wins", "total_trades", "total_profit", "active"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data.values():
            writer.writerow(row)

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
    profit = 0.0
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
            # Simulate closing the position shortly after for demo purposes
            time.sleep(1)
            try:
                latest_trade = api.get_latest_trade(symbol)
                close_price = float(latest_trade.price)
                profit = close_price - price
                print(f"Closing price: ${close_price}")
            except Exception as e:
                print(f"Failed to fetch closing price: {e}")
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
            profit,
        ])

    update_strategy_stats(strategy_used, profit)

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
