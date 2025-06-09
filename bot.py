"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from typing import Optional, List

from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import requests
import openai

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def news_risk_filter(symbol: str) -> Optional[str]:
    """Return GPT classification of recent news for the symbol."""
    if not NEWS_API_KEY or not OPENAI_API_KEY:
        print("Missing NewsAPI or OpenAI credentials.")
        return None

    url = (
        "https://newsapi.org/v2/everything"
        f"?q={symbol}&sortBy=publishedAt&language=en&apiKey={NEWS_API_KEY}"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"NewsAPI request failed: {exc}")
        return None

    headlines: List[str] = [a.get("title", "") for a in data.get("articles", [])][:5]
    if not headlines:
        print("No headlines found.")
        classification = "neutral"
    else:
        openai.api_key = OPENAI_API_KEY
        prompt = (
            "Classify the following stock news headlines as 'risky', 'neutral', or 'positive'.\n"
            + "\n".join(f"- {h}" for h in headlines)
        )
        try:
            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
            )
            classification = chat["choices"][0]["message"]["content"].strip().lower()
        except Exception as exc:
            print(f"OpenAI request failed: {exc}")
            classification = "neutral"

    with open("news_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            symbol,
            " ; ".join(headlines),
            classification,
        ])

    return classification

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

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
