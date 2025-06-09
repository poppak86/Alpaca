"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import openai

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY


def analyst_brain(trade_logs: str) -> str:
    """Analyze past trades for patterns and improvement opportunities."""
    if not OPENAI_API_KEY:
        return "Missing OpenAI credentials."

    messages = [
        {
            "role": "system",
            "content": (
                "You are the trading analyst AI. Review trade logs and summarize"
                " notable patterns, successes, and failures. Suggest areas of"
                " improvement."
            ),
        },
        {"role": "user", "content": trade_logs},
    ]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message.content.strip()


def strategist_brain(market_context: str) -> str:
    """Generate new trading strategies from market context."""
    if not OPENAI_API_KEY:
        return "Missing OpenAI credentials."

    messages = [
        {
            "role": "system",
            "content": (
                "You are the lead strategist AI. Based on market data and"
                " current performance, craft a concise trading strategy."
            ),
        },
        {"role": "user", "content": market_context},
    ]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message.content.strip()


def news_brain(headlines: str) -> str:
    """Assess news headlines for sentiment and potential market impact."""
    if not OPENAI_API_KEY:
        return "Missing OpenAI credentials."

    messages = [
        {
            "role": "system",
            "content": (
                "You analyze financial news headlines and return a sentiment"
                " score with notes on how they might affect the market."
            ),
        },
        {"role": "user", "content": headlines},
    ]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message.content.strip()


def risk_brain(portfolio_state: str) -> str:
    """Evaluate the risk profile of the current portfolio."""
    if not OPENAI_API_KEY:
        return "Missing OpenAI credentials."

    messages = [
        {
            "role": "system",
            "content": (
                "You are the risk management AI. Examine the portfolio and"
                " recent trades to highlight major risks and position sizing"
                " concerns."
            ),
        },
        {"role": "user", "content": portfolio_state},
    ]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message.content.strip()

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
