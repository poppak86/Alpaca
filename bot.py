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
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def fetch_top_headlines(country: str = "us", limit: int = 3):
    """Return a list of top news headlines."""
    if not NEWS_API_KEY:
        print("Missing NEWS_API_KEY; skipping headlines fetch.")
        return []

    url = "https://newsapi.org/v2/top-headlines"
    params = {"country": country, "apiKey": NEWS_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        return [a.get("title") for a in articles][:limit]
    except Exception as exc:
        print(f"Failed to fetch headlines: {exc}")
        return []

def trade_and_log(symbol: str, strategy_used: str = "test_strategy"):
    """Trade any stock and log the decision, price, time, and logic used."""
    if not API_KEY or not SECRET_KEY:
        print("Missing Alpaca credentials.")
        return

    api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=BASE_URL)
    print(f"Watching {symbol.upper()}...")

    headlines = fetch_top_headlines()
    if headlines:
        print("Top headlines:")
        for hl in headlines:
            print(f"- {hl}")

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
            strategy_used,
            " | ".join(headlines)
        ])

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
