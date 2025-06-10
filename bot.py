"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime, date
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import requests

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"
EARNINGS_API_KEY = os.getenv("EARNINGS_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# FOMC meeting dates for 2024 (YYYY-MM-DD)
FOMC_DATES = {
    "2024-01-30", "2024-01-31",
    "2024-03-19", "2024-03-20",
    "2024-04-30", "2024-05-01",
    "2024-06-11", "2024-06-12",
    "2024-07-30", "2024-07-31",
    "2024-09-17", "2024-09-18",
    "2024-11-06", "2024-11-07",
    "2024-12-17", "2024-12-18",
}

def is_fomc_day(check_date: date | None = None) -> bool:
    """Return True if the given date falls on a scheduled FOMC meeting."""
    check_date = check_date or date.today()
    return check_date.isoformat() in FOMC_DATES


def has_earnings_today(symbol: str, check_date: date | None = None) -> bool:
    """Check if the given symbol reports earnings on the date."""
    check_date = check_date or date.today()
    if not EARNINGS_API_KEY:
        print("Missing EARNINGS_API_KEY. Skipping earnings check.")
        return False

    url = (
        "https://financialmodelingprep.com/api/v3/earning_calendar/"
        f"{symbol}?apikey={EARNINGS_API_KEY}"
    )
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            for item in resp.json():
                if item.get("date") == check_date.isoformat():
                    return True
        else:
            print(f"Earnings API error: {resp.status_code}")
    except Exception as exc:
        print(f"Failed to fetch earnings calendar: {exc}")
    return False


NEGATIVE_WORDS = {
    "crash",
    "loss",
    "fraud",
    "bankrupt",
    "collapse",
    "slump",
    "warning",
}


def has_negative_news(symbol: str) -> bool:
    """Simple sentiment check on recent news headlines."""
    if not NEWS_API_KEY:
        print("Missing NEWS_API_KEY. Skipping news sentiment check.")
        return False

    url = (
        "https://newsapi.org/v2/everything?" f"q={symbol}&pageSize=5&apiKey={NEWS_API_KEY}"
    )
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            articles = resp.json().get("articles", [])
            score = 0
            for art in articles:
                title = art.get("title", "").lower()
                if any(word in title for word in NEGATIVE_WORDS):
                    score += 1
            return score >= 2
        else:
            print(f"News API error: {resp.status_code}")
    except Exception as exc:
        print(f"Failed to fetch news: {exc}")
    return False


def high_risk(symbol: str) -> bool:
    """Return True if any high-risk condition is detected."""
    if is_fomc_day():
        print("FOMC day detected. Avoiding trade.")
        return True
    if has_earnings_today(symbol):
        print("Earnings report day detected. Avoiding trade.")
        return True
    if has_negative_news(symbol):
        print("Negative news sentiment detected. Avoiding trade.")
        return True
    return False

def trade_and_log(symbol: str, strategy_used: str = "test_strategy"):
    """Trade any stock and log the decision, price, time, and logic used."""
    if not API_KEY or not SECRET_KEY:
        print("Missing Alpaca credentials.")
        return

    if high_risk(symbol):
        # Do not proceed with trading
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

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
