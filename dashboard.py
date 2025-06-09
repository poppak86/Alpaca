import csv
from collections import Counter
from typing import List


def generate_dashboard(log_file: str = "trade_log.csv") -> None:
    """Print a simple dashboard of trading performance.

    The CSV is expected to have headers including 'profit' for each trade and
    'strategy_used' indicating which strategy initiated the trade. If these
    columns are missing, zeros or blanks are assumed.
    """
    trades: List[dict] = []
    try:
        with open(log_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                trades.append(row)
    except FileNotFoundError:
        print(f"Log file '{log_file}' not found.")
        return

    if not trades:
        print("No trade data available.")
        return

    profits: List[float] = []
    strategies: List[str] = []
    wins = 0
    for row in trades:
        profit = float(row.get("profit", 0))
        strategy = row.get("strategy_used", row.get("strategy", ""))
        profits.append(profit)
        strategies.append(strategy)
        if profit > 0:
            wins += 1

    total_trades = len(trades)
    avg_profit = sum(profits) / total_trades
    win_rate = (wins / total_trades) * 100
    most_used_strategy = Counter(strategies).most_common(1)[0][0] if strategies else "N/A"

    print("=== Trading Dashboard ===")
    print(f"Trades analyzed: {total_trades}")
    print(f"Win rate: {win_rate:.2f}%")
    print(f"Average profit: ${avg_profit:.2f}")
    print(f"Most used strategy: {most_used_strategy}")
    print(f"Trade volume: {total_trades}")


if __name__ == "__main__":
    generate_dashboard()
