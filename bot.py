"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

def trade_and_log(
    symbol: str,
    stop_loss: float,
    take_profit: float,
    strategy_used: str = "test_strategy",
):
    """Trade any stock and log the decision, price, time, logic used, and R:R."""
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

    risk = price - stop_loss
    reward = take_profit - price
    if risk <= 0 or reward <= 0:
        print("Invalid stop loss or take profit levels.")
        return
    rr_ratio = reward / risk
    print(f"Risk-reward ratio: {rr_ratio:.2f}")

    response = None
    if rr_ratio < 1.5:
        print("R:R ratio below 1.5. Trade skipped.")
    elif price < 500:  # Placeholder logic
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
            strategy_used,
            rr_ratio
        ])

if __name__ == "__main__":
    # Example usage with placeholder stop loss and take profit levels
    trade_and_log("AAPL", stop_loss=480.0, take_profit=510.0, strategy_used="price_under_500")
