"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
import math
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"


def calculate_position_size(max_risk_per_trade: float, entry_price: float, stop_loss_price: float) -> int:
    """Return share size based on risk tolerance.

    position_size = max_risk_per_trade / (entry_price - stop_loss_price)
    Result is floored to the nearest whole share.
    """
    risk_per_share = entry_price - stop_loss_price
    if risk_per_share <= 0:
        raise ValueError("Entry price must be greater than stop loss price.")

    size = max_risk_per_trade / risk_per_share
    return math.floor(size)

def trade_and_log(
    symbol: str,
    strategy_used: str = "test_strategy",
    max_risk_per_trade: float = 0.0,
    stop_loss_price: Optional[float] = None,
) -> None:
    """Trade any stock based on risk and log the decision."""
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

    if stop_loss_price is None:
        print("Stop loss price required for position sizing.")
        return

    try:
        position_size = calculate_position_size(max_risk_per_trade, price, stop_loss_price)
    except ValueError as e:
        print(f"Invalid risk parameters: {e}")
        return

    if position_size < 1:
        print("Position size below 1 share based on risk. No order placed.")
        position_size = 0
        response = None
    elif price < 500:  # Placeholder logic
        try:
            response = api.submit_order(
                symbol=symbol,
                qty=position_size,
                side="buy",
                type="market",
                time_in_force="gtc",
            )
            print(f"Buy order placed for {position_size} shares.")
        except Exception as e:
            print(f"Order failed: {e}")
    else:
        print("Price too high. No order placed.")
        response = None

    # Log everything for future learning
    with open("trade_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            symbol,
            price,
            "buy" if response else "skipped",
            strategy_used,
            position_size,
        ])

if __name__ == "__main__":
    # Example usage with $100 risk and a $5 stop loss distance
    trade_and_log("AAPL", "price_under_500", max_risk_per_trade=100, stop_loss_price=495)
