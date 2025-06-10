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
   pip install alpaca_trade_api python-dotenv pandas requests beautifulsoup4
```
2. Set additional environment variables for risk checks:
   - `EARNINGS_API_KEY` for earnings calendar access
   - `NEWS_API_KEY` for news sentiment analysis
