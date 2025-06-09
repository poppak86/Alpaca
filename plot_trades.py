import pandas as pd
import matplotlib.pyplot as plt
import sys

def plot_strategy(strategy: str, log_path: str = "trade_log.csv") -> None:
    """Plot buy prices for a given strategy and show average buy price."""
    df = pd.read_csv(log_path, header=None, names=[
        "timestamp", "symbol", "price", "action", "strategy"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    strategy_df = df[(df["strategy"] == strategy) & (df["action"] == "buy")]
    if strategy_df.empty:
        print(f"No buys found for strategy '{strategy}'.")
        return

    avg_price = strategy_df["price"].mean()

    plt.plot(strategy_df["timestamp"], strategy_df["price"], marker="o", label="Buy Price")
    plt.axhline(avg_price, color="red", linestyle="--", label=f"Average Buy: {avg_price:.2f}")
    plt.xlabel("Timestamp")
    plt.ylabel("Price")
    plt.title(f"Trades for Strategy: {strategy}")
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    strategy_arg = sys.argv[1] if len(sys.argv) > 1 else "test_strategy"
    plot_strategy(strategy_arg)
