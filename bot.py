"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import requests
import time

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"


def submit_order_with_retry(api: tradeapi.REST, max_attempts: int = 3, **order_kwargs):
    """Submit an order and retry on network or API errors up to max_attempts."""
    attempts = 0
    last_error = ""
    while attempts < max_attempts:
        try:
            response = api.submit_order(**order_kwargs)
            print("Buy order placed.")
            return response, attempts + 1, ""
        except tradeapi.rest.APIError as e:
            message = str(e)
            # Do not retry logical errors
            if "insufficient" in message.lower() or "buying power" in message.lower():
                print(f"Order failed: {message}")
                return None, attempts + 1, message
            attempts += 1
            last_error = message
            print(f"API error on attempt {attempts}: {message}")
        except requests.exceptions.RequestException as e:
            attempts += 1
            last_error = str(e)
            print(f"Network error on attempt {attempts}: {e}")

        if attempts < max_attempts:
            time.sleep(1)

    print(f"All {attempts} attempts failed. Error: {last_error}")
    return None, attempts, last_error

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
    attempts = 0
    error_message = ""
    if price < 500:  # Placeholder logic
        response, attempts, error_message = submit_order_with_retry(
            api,
            symbol=symbol,
            qty=1,
            side="buy",
            type="market",
            time_in_force="gtc",
        )
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
            attempts,
            error_message
        ])

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
