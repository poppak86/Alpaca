"""Self-learning AI trading bot starter using Alpaca."""

import os
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import requests
import openai
import schedule
import time

load_dotenv()

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


def fetch_headlines(limit: int = 5) -> list[str]:
    """Return a list of top U.S. news headlines."""
    key = os.getenv("NEWS_API_KEY")
    if not key:
        return []
    try:
        resp = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={"country": "us", "pageSize": limit, "apiKey": key},
            timeout=10,
        )
        data = resp.json()
        return [a.get("title", "") for a in data.get("articles", [])[:limit]]
    except Exception as e:
        print(f"Failed to fetch headlines: {e}")
        return []


def fetch_yesterday_trades() -> list[dict]:
    """Return trades from the previous UTC day."""
    if not os.path.exists("trade_log.csv"):
        return []
    trades = []
    yesterday = (datetime.utcnow() - timedelta(days=1)).date()
    with open("trade_log.csv", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 4:
                continue
            time_str, symbol, price, action = row[:4]
            try:
                t = datetime.fromisoformat(time_str)
            except Exception:
                continue
            if t.date() == yesterday:
                trades.append({
                    "time": time_str,
                    "symbol": symbol,
                    "price": price,
                    "action": action,
                })
    return trades


def send_telegram(message: str) -> None:
    """Send a text message via Telegram bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Missing Telegram credentials.")
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10)
        print("Telegram message sent.")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")


def send_daily_market_summary() -> None:
    """Gather data and send a daily market insight via Telegram."""
    headlines = fetch_headlines()
    trades = fetch_yesterday_trades()

    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("Missing OpenAI API key.")
        return

    prompt_parts = ["Top headlines:"]
    prompt_parts.extend(f"- {h}" for h in headlines)
    prompt_parts.append("\nYesterday's trades:")
    prompt_parts.extend(
        f"- {t['time']} {t['symbol']} {t['action']} at ${t['price']}" for t in trades
    )
    prompt_parts.append("\nProvide a short insight for trading today.")
    prompt = "\n".join(prompt_parts)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            timeout=15,
        )
        summary = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT request failed: {e}")
        return

    send_telegram(summary)


def schedule_daily_insight() -> None:
    """Run the market summary once per day at U.S. market open."""
    schedule.every().day.at("14:30").do(send_daily_market_summary)
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    trade_and_log("AAPL", "price_under_500")
    # Start the daily market summary scheduler
    # Comment this out if running in environments where a persistent
    # process is undesirable.
    schedule_daily_insight()
