# Alpaca AI Trading Bot

This project is the foundation for building the most advanced self-learning trading bot in the world.

Unlike basic bots that follow fixed strategies, this system is designed to evolve. It will:
- Trade **any U.S. stock or option** based on real-time data and patterns
- Simulate trades using **Alpaca’s paper trading API**
- Log every trade with full context: symbol, price, timestamp, indicator data, and relevant news
- Analyze its own performance after every trade to detect patterns in what works and what doesn’t
- Adjust its logic and improve over time — like a trader that never forgets and never stops learning

## 🔮 Long-Term Vision

This bot will:
- Autonomously discover the best indicators (e.g. RSI, MACD, volume spikes)
- Ingest and score **real-time news headlines** for sentiment and market impact
- Simulate and eventually execute **options strategies**
- Self-monitor its win rate and only go live when it consistently hits **90–95% profitability**
- Evolve into an intelligent trading system that can run indefinitely, adaptively, and profitably — even spawning child versions of itself to test new strategies

## 🧪 Current Phase (MVP)

- Connect to Alpaca Paper API
- Trade any stock
- Log detailed trade data to CSV
- Begin self-analysis loop on trade outcomes

## 🛠 Setup

1. Install dependencies:
   ```bash
   pip install alpaca_trade_api python-dotenv pandas requests
   ```

## 📊 Strategy Tracking

The bot now records the profit or loss from every trade in `trade_log.csv` and
aggregates statistics per strategy in `strategy_stats.csv`. When a strategy's
win rate falls below **40%** after 10 trades it is automatically marked as
inactive and a Telegram message is sent (configure `TELEGRAM_BOT_TOKEN` and
`TELEGRAM_CHAT_ID` in your `.env` file).
