"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime, timezone
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import openai

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

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
            strategy_used
        ])


def generate_daily_summary(log_file: str = "trade_log.csv", summary_file: str = "daily_summary.csv") -> None:
    """Compile daily stats at market close and write a GPT summary."""
    today = datetime.now(timezone.utc).date()
    trades = []

    if not os.path.exists(log_file):
        print(f"Log file {log_file} not found.")
        return

    with open(log_file, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            try:
                ts = datetime.fromisoformat(row[0]).date()
            except Exception:
                continue
            if ts == today:
                trades.append(row)

    total_trades = sum(1 for r in trades if len(r) > 3 and r[3] != "skipped")

    wins = 0
    losses = 0
    net_profit = 0.0
    for r in trades:
        if len(r) >= 6:
            try:
                profit = float(r[5])
            except ValueError:
                profit = 0.0
            net_profit += profit
            if profit > 0:
                wins += 1
            else:
                losses += 1

    win_loss_ratio = (wins / losses) if losses else (float(wins) if wins else 0.0)

    summary_prompt = (
        f"Summarize today's trading activity. We made {total_trades} trades with a "
        f"win/loss ratio of {win_loss_ratio:.2f} and net profit of ${net_profit:.2f}."
    )

    gpt_summary = ""
    if OPENAI_API_KEY:
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": summary_prompt}],
            )
            gpt_summary = resp.choices[0].message.content.strip().replace("\n", " ")
        except Exception as e:
            gpt_summary = f"GPT summarization failed: {e}"
    else:
        gpt_summary = "No OPENAI_API_KEY provided."

    with open(summary_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            today.isoformat(),
            total_trades,
            f"{win_loss_ratio:.2f}",
            f"{net_profit:.2f}",
            gpt_summary,
        ])

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
    generate_daily_summary()
