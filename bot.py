"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
import time
from datetime import datetime
from typing import List

import requests
import openai
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

def fetch_news(symbol: str) -> List[str]:
    """Return recent news headlines for the symbol."""
    if not NEWS_API_KEY:
        return []
    url = (
        "https://newsapi.org/v2/everything?q="
        f"{symbol}&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [a.get("title", "") for a in data.get("articles", [])]
    except Exception as e:
        print(f"Failed to fetch news: {e}")
        return []

def summarize_trade(
    symbol: str,
    strategy: str,
    entry_price: float,
    exit_price: float,
    success: bool,
    news: List[str],
) -> str:
    """Use GPT to summarize the trade outcome."""
    if not OPENAI_API_KEY:
        print("Missing OpenAI API key. Skipping summary.")
        return ""
    openai.api_key = OPENAI_API_KEY
    outcome = "worked" if success else "didn't work"
    headlines = " | ".join(news)
    prompt = (
        f"We traded {symbol} using the strategy '{strategy}'. "
        f"Entry price was ${entry_price:.2f} and we checked at ${exit_price:.2f}. "
        f"The trade {outcome}. Relevant news headlines were: {headlines}. "
        "Give a short explanation of why the trade was successful or not based on the news and strategy."
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
        )
        return resp.choices[0].message["content"].strip()
    except Exception as e:
        print(f"Failed to get summary from OpenAI: {e}")
        return ""

def trade_and_log(
    symbol: str, strategy_used: str = "test_strategy", evaluation_delay: int = 5
):
    """Trade a stock, analyze outcome with GPT, and log everything."""
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

    news = fetch_news(symbol)

    exit_price = price
    success = False
    if response:
        time.sleep(evaluation_delay)
        try:
            latest = api.get_latest_trade(symbol)
            exit_price = float(latest.price)
            success = exit_price > price
        except Exception as e:
            print(f"Could not evaluate trade: {e}")

    summary = summarize_trade(
        symbol, strategy_used, price, exit_price, success, news
    )

    # Log everything for future learning
    with open("trade_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            symbol,
            price,
            exit_price,
            "buy" if response else "skipped",
            strategy_used,
            success,
            summary,
        ])

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
