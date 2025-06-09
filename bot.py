"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
import time
import random
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

def get_news_sentiment(symbol: str) -> str:
    """Return news sentiment for a symbol. Placeholder implementation."""
    # TODO: integrate real news sentiment analysis
    return "neutral"


def risk_brain_allows(symbol: str, price: float) -> bool:
    """Determine if risk management approves trading. Placeholder."""
    # TODO: integrate real risk analysis
    return True


def log_trade(symbol: str, price: float, action: str, strategy: str) -> None:
    """Append a record to the trade log."""
    with open("trade_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            symbol,
            price,
            action,
            strategy,
        ])


def trade_loop(symbol: str, price_threshold: float = 500, strategy: str = "price_under_threshold") -> None:
    """Continuously monitor and trade when all conditions are met."""
    if not API_KEY or not SECRET_KEY:
        print("Missing Alpaca credentials.")
        return

    api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=BASE_URL)
    print(f"Monitoring {symbol.upper()}...")

    last_trade_marker = None

    while True:
        try:
            clock = api.get_clock()
            if not clock.is_open:
                print("Market closed. Waiting...")
                time.sleep(60)
                continue
        except Exception as e:
            print(f"Clock error: {e}")
            time.sleep(60)
            continue

        try:
            price = float(api.get_latest_trade(symbol).price)
            print(f"Current price: ${price}")
        except Exception as e:
            print(f"Failed to fetch price for {symbol}: {e}")
            time.sleep(15)
            continue

        sentiment = get_news_sentiment(symbol)
        risk_ok = risk_brain_allows(symbol, price)

        strategy_ok = price < price_threshold
        conditions_met = strategy_ok and sentiment in {"positive", "neutral"} and risk_ok
        current_marker = (price, sentiment, risk_ok)

        if conditions_met:
            if current_marker != last_trade_marker:
                try:
                    api.submit_order(
                        symbol=symbol,
                        qty=1,
                        side="buy",
                        type="market",
                        time_in_force="gtc",
                    )
                    print("Buy order placed.")
                    log_trade(symbol, price, "buy", strategy)
                    last_trade_marker = current_marker
                except Exception as e:
                    print(f"Order failed: {e}")
            else:
                print("Conditions unchanged since last trade. Skipping.")
        else:
            print("Conditions not met. No trade placed.")

        time.sleep(random.uniform(10, 15))

if __name__ == "__main__":
    trade_loop("AAPL")
