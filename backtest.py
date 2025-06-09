import json
import os
import random


def example_strategy(_):
    """Placeholder strategy that randomly wins or loses."""
    return random.choice([True, False])


def run_backtest(strategy_func, trials=100):
    """Run a simple backtest returning win rate."""
    wins = sum(strategy_func(None) for _ in range(trials))
    return wins / trials


def main():
    strategies = {
        "ma_crossover": example_strategy,
        "rsi_reversal": example_strategy,
        "buy_and_hold": example_strategy,
    }

    scores = {}
    if os.path.exists("strategy_scores.json"):
        with open("strategy_scores.json", "r") as f:
            try:
                scores = json.load(f)
            except json.JSONDecodeError:
                scores = {}

    for name, func in strategies.items():
        win_rate = run_backtest(func)
        print(f"{name} win rate: {win_rate:.2%}")
        scores[name] = win_rate

    with open("strategy_scores.json", "w") as f:
        json.dump(scores, f, indent=2)
        f.write("\n")
    print("Updated strategy_scores.json")


if __name__ == "__main__":
    main()
