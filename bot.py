"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

PAPER_URL = "https://paper-api.alpaca.markets"
LIVE_URL = "https://api.alpaca.markets"

STATE_FILE = "mode.json"

def load_state() -> dict:
    """Return mode state from file or defaults."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"mode": "live", "fail_count": 0, "paper_until": None}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def send_telegram_alert(message: str) -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram credentials missing.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": message})
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")


def switch_mode(reason: str) -> None:
    """Toggle between live and paper trading modes."""
    state = load_state()
    if state["mode"] == "live":
        state["mode"] = "paper"
        state["paper_until"] = (
            datetime.utcnow() + timedelta(hours=1)
        ).isoformat()
    else:
        state["mode"] = "live"
        state["paper_until"] = None
    state["fail_count"] = 0
    save_state(state)
    message = f"Switching to {state['mode']} mode: {reason}"
    print(message)
    send_telegram_alert(message)

def trade_and_log(symbol: str, strategy_used: str = "test_strategy") -> None:
    """Trade any stock and log the decision, price, time, and logic used."""
    if not API_KEY or not SECRET_KEY:
        print("Missing Alpaca credentials.")
        return

    state = load_state()
    base_url = LIVE_URL if state["mode"] == "live" else PAPER_URL
    api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=base_url)
    print(
        f"{state['mode'].capitalize()} mode using {base_url}. Watching {symbol.upper()}..."
    )

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

    success = response is not None
    if success:
        state["fail_count"] = 0
        if (
            state["mode"] == "paper"
            and state.get("paper_until")
            and datetime.utcnow() >= datetime.fromisoformat(state["paper_until"])
        ):
            switch_mode("Successful paper trade after cooldown")
            state = load_state()
    else:
        state["fail_count"] += 1
        if state["mode"] == "live" and state["fail_count"] >= 3:
            switch_mode("3 consecutive failed trades")
            state = load_state()

    save_state(state)

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

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")

