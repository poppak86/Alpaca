"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
import requests
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
EASTERN = ZoneInfo("US/Eastern")


def send_telegram_message(message: str) -> None:
    """Send a text message to the configured Telegram chat."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing Telegram credentials.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload, timeout=10)
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
    with open("trade_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            symbol,
            price,
            "buy" if response else "skipped",
            strategy_used
        ])


def send_daily_summary() -> None:
    """Compile today's trade data and send a brief summary to Telegram."""
    today = datetime.now(EASTERN).date()
    buys = sells = skips = 0
    net = 0.0
    open_positions: dict[str, list[float]] = {}
    profits: list[float] = []

    if not os.path.exists("trade_log.csv"):
        print("No trade log found to summarize.")
        return

    with open("trade_log.csv", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 4:
                continue
            timestamp, symbol, price, action = row[:4]
            try:
                entry_date = datetime.fromisoformat(timestamp).date()
            except ValueError:
                continue
            if entry_date != today:
                continue
            price = float(price)

            if action == "buy":
                buys += 1
                open_positions.setdefault(symbol, []).append(price)
            elif action == "sell":
                sells += 1
                if open_positions.get(symbol):
                    buy_price = open_positions[symbol].pop(0)
                    profit = price - buy_price
                    profits.append(profit)
                    net += profit
                else:
                    net += price
            else:
                skips += 1

    win_rate_msg = "N/A"
    if profits:
        wins = sum(1 for p in profits if p > 0)
        win_rate_msg = f"{wins / len(profits) * 100:.2f}%"

    summary = (
        f"Daily Summary ({today}):\n"
        f"Buys: {buys}\n"
        f"Sells: {sells}\n"
        f"Skips: {skips}\n"
        f"Win Rate: {win_rate_msg}\n"
        f"Net P/L: {net:.2f}"
    )

    send_telegram_message(summary)

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
    now_est = datetime.now(EASTERN)
    if now_est.time() >= time(16, 0):
        send_daily_summary()
