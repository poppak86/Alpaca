import os
import csv
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from openai import OpenAI

load_dotenv()


def send_daily_summary() -> str:
    """Placeholder daily summary function."""
    return "Daily summary placeholder."


def _read_last_trade() -> str:
    try:
        with open("trade_log.csv", newline="") as f:
            rows = list(csv.reader(f))
            if not rows:
                return "Trade log is empty."
            last = rows[-1]
            return (
                f"Time: {last[0]}\n"
                f"Symbol: {last[1]}\n"
                f"Price: {last[2]}\n"
                f"Action: {last[3]}\n"
                f"Strategy: {last[4]}"
            )
    except FileNotFoundError:
        return "trade_log.csv not found."


def last_trade(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(_read_last_trade())


def summary(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(send_daily_summary())


def chat_with_gpt(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OpenAI API key is not configured."
    client = OpenAI(api_key=api_key)
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:  # pragma: no cover - network call
        return f"Error contacting OpenAI: {e}"


def answer(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(chat_with_gpt(update.message.text))


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("TELEGRAM_BOT_TOKEN not set.")
        return
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("lasttrade", last_trade))
    dp.add_handler(CommandHandler("summary", summary))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, answer))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
