"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
import time
from datetime import datetime, date
from dotenv import load_dotenv
import requests
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def fetch_headlines(symbol: str) -> list:
    """Return today's top news headlines for the given symbol."""
    if not NEWS_API_KEY:
        return []

    today = date.today().isoformat()
    url = (
        "https://newsapi.org/v2/everything"
        f"?q={symbol}&from={today}&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    )

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return [a.get("title", "") for a in data.get("articles", [])][:5]
    except Exception as e:  # pragma: no cover - best effort
        print(f"Failed to fetch headlines: {e}")
        return []


def news_brain(trade_data: dict, headlines: list) -> None:
    """Placeholder to analyze if headlines predicted the trade outcome."""
    print("news_brain analyzing:", trade_data)
    for hl in headlines:
        print(" -", hl)


def risk_brain(trade_data: dict, headlines: list) -> None:
    """Placeholder to further analyze trade risk."""
    print("risk_brain evaluating:", trade_data)

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

    time.sleep(2)
    try:
        exit_trade = api.get_latest_trade(symbol)
        exit_price = float(exit_trade.price)
    except Exception as e:  # pragma: no cover - best effort
        print(f"Failed to fetch exit price: {e}")
        exit_price = price

    action = "buy" if response else "skipped"
    headlines = fetch_headlines(symbol)

    # Log everything for future learning
    with open("trade_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            symbol,
            price,
            action,
            strategy_used,
            exit_price,
            "|".join(headlines),
        ])

    if response and exit_price < price:
        trade_data = {
            "symbol": symbol,
            "entry_price": price,
            "exit_price": exit_price,
            "strategy": strategy_used,
        }
        news_brain(trade_data, headlines)
        risk_brain(trade_data, headlines)

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
