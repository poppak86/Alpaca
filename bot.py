"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import yfinance as yf

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"
DANGER_VIX_THRESHOLD = float(os.getenv("DANGER_VIX_THRESHOLD", "30"))


def get_vix_value() -> float | None:
    """Fetch the latest VIX value using yfinance."""
    try:
        vix = yf.Ticker("^VIX")
        data = vix.history(period="1d")
        if not data.empty:
            return float(data["Close"].iloc[-1])
    except Exception as exc:
        print(f"Failed to fetch VIX data: {exc}")
    return None

def trade_and_log(symbol: str, strategy_used: str = "test_strategy"):
    """Trade any stock and log the decision, price, time, and logic used."""
    if not API_KEY or not SECRET_KEY:
        print("Missing Alpaca credentials.")
        return

    api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=BASE_URL)
    print(f"Watching {symbol.upper()}...")

    vix = get_vix_value()
    if vix is not None and vix > DANGER_VIX_THRESHOLD:
        print(
            f"High volatility detected: VIX {vix} > {DANGER_VIX_THRESHOLD}. Halting trade."
        )
        with open("trade_log.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.utcnow().isoformat(),
                symbol,
                "N/A",
                "skipped",
                strategy_used,
                vix,
                "vix_above_threshold",
            ])
        return

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
            strategy_used,
            vix,
            ""
        ])

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
