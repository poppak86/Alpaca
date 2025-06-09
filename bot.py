"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import requests

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_trade_alert(
    action: str,
    symbol: str,
    strategy: str,
    trade_type: str,
    price: float,
    quantity: int,
    pl: float | None = None,
    expiration: str | None = None,
    strike: float | None = None,
    option_type: str | None = None,
) -> None:
    """Send a Telegram alert with trade details for stocks or options."""

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    is_option = trade_type.lower() == "option" or (
        expiration and strike and option_type
    )

    if is_option:
        contract = f"{symbol} {expiration} {strike}{option_type.upper()}"
        message = (
            f"{action.upper()} {quantity} contract(s) of {contract} using "
            f"{strategy} at ${price:.2f}"
        )
    else:
        message = (
            f"{action.upper()} {quantity} share(s) of {symbol} using {strategy} "
            f"at ${price:.2f}"
        )

    if pl is not None:
        message += f" | P/L: ${pl:.2f}"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    except Exception as exc:
        print(f"Failed to send Telegram alert: {exc}")

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
    action = "buy" if price < 500 else "sell"
    try:
        response = api.submit_order(
            symbol=symbol,
            qty=1,
            side=action,
            type="market",
            time_in_force="gtc",
        )
        print("Buy order placed." if action == "buy" else "Sell order placed.")

        pl = None
        if action == "sell":
            try:
                with open("trade_log.csv", newline="") as f:
                    rows = [r for r in csv.reader(f) if r[1] == symbol and r[3] == "buy"]
                    if rows:
                        last_buy_price = float(rows[-1][2])
                        pl = price - last_buy_price
            except FileNotFoundError:
                pass

        send_trade_alert(
            action=action,
            symbol=symbol,
            strategy=strategy_used,
            trade_type="stock",
            price=price,
            quantity=1,
            pl=pl,
        )
    except Exception as e:
        print(f"Order failed: {e}")

    # Log everything for future learning
    with open("trade_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            symbol,
            price,
            action if response else "skipped",
            strategy_used,
        ])

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
