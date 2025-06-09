"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime, timezone
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import pandas_market_calendars as mcal

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

# Predefined dates of upcoming FOMC announcements (YYYY-MM-DD). In practice
# this should be fetched from an external calendar.
FOMC_DATES = {
    "2024-06-12",
    "2024-07-31",
    "2024-09-18",
    "2024-11-07",
    "2024-12-18",
}

def trade_and_log(symbol: str, strategy_used: str = "test_strategy"):
    """Trade any stock and log the decision, price, time, and logic used."""
    today = datetime.now(timezone.utc).date()
    nyse = mcal.get_calendar("NYSE")
    # Skip trading on weekends and market holidays
    sched = nyse.schedule(start_date=today, end_date=today)
    if sched.empty:
        print("Market closed today. Skipping trading.")
        return

    close_time = sched.iloc[0]["market_close"].tz_convert("America/New_York")
    low_volume = False
    notes = []
    if close_time.hour < 16:
        low_volume = True
        notes.append("half-day")
        print("Early close detected. Low volume expected.")

    if today.isoformat() in FOMC_DATES:
        low_volume = True
        notes.append("FOMC")
        print("FOMC announcement today. Volume may be lower.")
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
            datetime.now(timezone.utc).isoformat(),
            symbol,
            price,
            "buy" if response else "skipped",
            strategy_used,
            "low_volume" if low_volume else "normal_volume",
            "|".join(notes)
        ])

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
