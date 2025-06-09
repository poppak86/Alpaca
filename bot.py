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
NEWS_API_KEY = os.getenv("NEWSAPI_KEY")

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


def get_headlines():
    """Fetch top stock market news from NewsAPI and log timestamp + headline."""
    if not NEWS_API_KEY:
        print("Missing NewsAPI key.")
        return

    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "q": "stock market",
        "language": "en",
        "apiKey": NEWS_API_KEY,
        "pageSize": 5,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        news = resp.json()
    except Exception as e:
        print(f"Failed to fetch news: {e}")
        return

    articles = news.get("articles", [])
    if not articles:
        print("No news articles found.")
        return

    with open("news_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        for article in articles:
            headline = article.get("title")
            if headline:
                writer.writerow([datetime.utcnow().isoformat(), headline])

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
    get_headlines()
