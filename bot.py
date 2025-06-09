"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import pandas as pd
import openai

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

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

def gpt_self_critique(trades_path: str = "trade_log.csv", critique_path: str = "critique_log.csv", trades_to_analyze: int = 5) -> None:
    """Summarize recent trades and ask GPT for improvement suggestions."""
    if not os.path.exists(trades_path):
        print(f"No trade log found at {trades_path}")
        return

    try:
        df = pd.read_csv(trades_path)
    except Exception as e:
        print(f"Failed to read trade log: {e}")
        return

    if df.empty:
        print("Trade log is empty.")
        return

    recent = df.tail(trades_to_analyze)
    summary = recent.to_csv(index=False)

    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("Missing OpenAI API key.")
        return

    prompt = f"Review these trades and suggest what could've been done better:\n{summary}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        critique = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT request failed: {e}")
        return

    with open(critique_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.utcnow().isoformat(), critique])
    print("Critique saved.")

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
    gpt_self_critique()
