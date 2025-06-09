from dataclasses import dataclass
import random

@dataclass
class Decision:
    vote: str  # 'buy' or 'skip'
    reason: str

class Brain:
    """Base class for trading brains."""
    name: str

    def decide(self, symbol: str, price: float) -> Decision:
        raise NotImplementedError

class CheapStockBrain(Brain):
    def __init__(self, threshold: float = 500.0):
        self.name = "cheap_stock_brain"
        self.threshold = threshold

    def decide(self, symbol: str, price: float) -> Decision:
        if price < self.threshold:
            return Decision("buy", f"price {price} < {self.threshold}")
        return Decision("skip", f"price {price} >= {self.threshold}")

class RandomBrain(Brain):
    def __init__(self):
        self.name = "random_brain"

    def decide(self, symbol: str, price: float) -> Decision:
        if random.random() > 0.5:
            return Decision("buy", "random choice buy")
        return Decision("skip", "random choice skip")


def plot_brain_votes(csv_path: str = "brain_votes.csv") -> None:
    """Plot vote counts from the brain vote log."""
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
    except ImportError:
        print("Install pandas and matplotlib to enable plotting.")
        return

    cols = ["timestamp", "symbol", "brain", "vote", "reason"]
    df = pd.read_csv(csv_path, names=cols)
    counts = df.groupby(["brain", "vote"]).size().unstack(fill_value=0)
    counts.plot(kind="bar", stacked=True)
    plt.title("Brain Vote Counts")
    plt.xlabel("Brain")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()
