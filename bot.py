"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
import json
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
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


def _summarize_performance(csv_file: str) -> str:
    """Create a short summary of recent performance from the log."""
    if not os.path.exists(csv_file):
        return "No performance data available."
    try:
        with open(csv_file, "r") as f:
            lines = f.readlines()[-10:]
        return "\n".join(line.strip() for line in lines)
    except Exception as e:
        return f"Failed to read performance data: {e}"


def generate_strategy_with_gpt(performance_csv: str = "trade_log.csv",
                               output_file: str = "proposed_strategies.json") -> Dict[str, str]:
    """Use GPT to propose a new trading strategy based on performance data."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("Missing OPENAI_API_KEY environment variable")

    openai.api_key = openai_api_key

    summary = _summarize_performance(performance_csv)
    prompt = (
        "You are a trading strategy generator. "
        "Based on the following recent performance data, propose a new trading "
        "strategy in a short JSON description.\n\n" + summary
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    strategy_text = response.choices[0].message.content.strip()

    new_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "strategy": strategy_text,
    }

    strategies: List[Dict[str, str]] = []
    if os.path.exists(output_file):
        try:
            with open(output_file, "r") as f:
                strategies = json.load(f)
        except Exception:
            strategies = []

    strategies.append(new_entry)

    with open(output_file, "w") as f:
        json.dump(strategies, f, indent=2)

    return new_entry

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
    try:
        result = generate_strategy_with_gpt()
        print("Proposed new strategy:")
        print(result["strategy"])
    except Exception as e:
        print(f"Strategy generation failed: {e}")
