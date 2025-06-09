"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

from account import (
    load_account,
    save_account,
    process_settlements,
    deduct_cash,
    add_pending_settlement,
    add_position,
    remove_position,
)

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

def trade_and_log(symbol: str, strategy_used: str = "test_strategy"):
    """Trade any stock and log the decision, price, time, and logic used."""
    if not API_KEY or not SECRET_KEY:
        print("Missing Alpaca credentials.")
        return

    account = process_settlements(load_account())
    if account.get("cash", 0) < 1:
        print("Insufficient cash to trade today.")
        save_account(account)
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
    side = "skipped"
    trade_cost = price * 1  # buying one share
    if price < 500:  # Placeholder buy logic
        if deduct_cash(account, trade_cost):
            try:
                response = api.submit_order(
                    symbol=symbol,
                    qty=1,
                    side="buy",
                    type="market",
                    time_in_force="gtc",
                )
                add_position(account, symbol, 1)
                side = "buy"
                print("Buy order placed.")
            except Exception as e:
                print(f"Order failed: {e}")
                account["cash"] += trade_cost
        else:
            print("Not enough settled cash for trade.")
    elif price > 520 and account.get("positions", {}).get(symbol, 0) > 0:
        try:
            response = api.submit_order(
                symbol=symbol,
                qty=1,
                side="sell",
                type="market",
                time_in_force="gtc",
            )
            remove_position(account, symbol, 1)
            add_pending_settlement(account, price)
            side = "sell"
            print("Sell order placed.")
        except Exception as e:
            print(f"Order failed: {e}")
    else:
        print("No trading action taken.")

    save_account(account)

    # Log everything for future learning
    with open("trade_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            symbol,
            price,
            side if response else "skipped",
            strategy_used,
        ])

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
