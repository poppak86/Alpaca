"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from typing import List
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

from brains import CheapStockBrain, RandomBrain, Decision

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

    # Evaluate brains
    brains = [CheapStockBrain(), RandomBrain()]
    timestamp = datetime.utcnow().isoformat()
    votes: List[Decision] = []
    for brain in brains:
        decision = brain.decide(symbol, price)
        votes.append(decision)
        print(f"{brain.name} voted {decision.vote}: {decision.reason}")

    buy_votes = sum(1 for v in votes if v.vote == "buy")
    final_decision = "buy" if buy_votes > len(votes) / 2 else "skip"

    response = None
    if final_decision == "buy":
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
        print("Brains voted against buying. No order placed.")

    # Log brain votes for traceability
    with open("brain_votes.csv", "a", newline="") as f:
        writer = csv.writer(f)
        for brain, decision in zip(brains, votes):
            writer.writerow([
                timestamp,
                symbol,
                brain.name,
                decision.vote,
                decision.reason,
            ])

    # Log everything for future learning
    with open("trade_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp,
            symbol,
            price,
            "buy" if response else "skipped",
            strategy_used
        ])

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
