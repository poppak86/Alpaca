"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import requests
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

KEYWORDS = [
    "Jerome Powell",
    "Fed",
    "inflation",
    "CPI",
    "earnings",
]


def fetch_top_headlines(count: int = 5) -> list[str]:
    """Return the day's top headlines using NewsAPI."""
    if not NEWS_API_KEY:
        print("NEWS_API_KEY not set, skipping headline fetch.")
        return []

    try:
        url = "https://newsapi.org/v2/top-headlines"
        params = {"country": "us", "pageSize": count, "apiKey": NEWS_API_KEY}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        return [a.get("title", "") for a in data.get("articles", [])][:count]
    except Exception as e:
        print(f"Failed to fetch headlines: {e}")
        return []


def news_brain(summary: str) -> None:
    """Placeholder to process risky news before trading."""
    print(f"Sending to news_brain: {summary}")


def check_headlines_for_risk(headlines: list[str]) -> tuple[int, str]:
    """Check headlines for risky keywords."""
    flagged = []
    risk = 0
    for h in headlines:
        for kw in KEYWORDS:
            if kw.lower() in h.lower():
                flagged.append(h)
                risk += 1
                break
    return risk, "; ".join(flagged)

def trade_and_log(symbol: str, strategy_used: str = "test_strategy"):
    """Trade any stock and log the decision, price, time, and logic used."""
    if not API_KEY or not SECRET_KEY:
        print("Missing Alpaca credentials.")
        return

    risk_score = 0
    headlines = fetch_top_headlines()
    risk_add, summary = check_headlines_for_risk(headlines)
    risk_score += risk_add
    if risk_add:
        news_brain(summary)
    print(f"Risk score: {risk_score}")

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
