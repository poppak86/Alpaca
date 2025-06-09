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
    strategy_used: str = "test_strategy",
    price: float | None = None,
    simulate: bool = False,
    api: tradeapi.REST | None = None,
):
    """Trade any stock and log the decision, price, time, and logic used.

    Parameters
    ----------
    symbol: str
        The ticker to trade.
    strategy_used: str
        Description of the strategy or run.
    price: float | None, optional
        If provided, use this price instead of fetching the latest trade price.
    simulate: bool, optional
        When True, skip actual order submission and only log the result.
    api: tradeapi.REST | None, optional
        Existing Alpaca REST client. If not provided, one will be created.
    """
    if not API_KEY or not SECRET_KEY:
        print("Missing Alpaca credentials.")
        return

    if api is None:
        api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=BASE_URL)

    print(f"Watching {symbol.upper()}...")

    try:
        if price is None:
            latest_trade = api.get_latest_trade(symbol)
            price = float(latest_trade.price)
        print(f"Current price: ${price}")
    except Exception as e:
        print(f"Failed to fetch price for {symbol}: {e}")
        return

    response = None
    if price < 500:  # Placeholder logic
        if simulate:
            response = True
            print("Simulated buy order.")
        else:
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


def backtest(symbol: str, start: str, end: str, timeframe: str = "1Day", strategy_used: str = "backtest"):
    """Download historical data and run trade_and_log over it to simulate trades."""
    if not API_KEY or not SECRET_KEY:
        print("Missing Alpaca credentials.")
        return

    api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=BASE_URL)

    try:
        bars = api.get_bars(symbol, timeframe, start=start, end=end).df
    except Exception as e:
        print(f"Failed to fetch historical data: {e}")
        return

    for _, bar in bars.iterrows():
        trade_and_log(
            symbol,
            strategy_used=strategy_used,
            price=float(bar['close']),
            simulate=True,
            api=api,
        )

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
