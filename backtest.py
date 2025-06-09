import math
from typing import Callable, List

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def simulate_historical_trades(prices: pd.Series, strategy: Callable[[float], str]) -> pd.Series:
    """Simulate trades over historical prices using a simple strategy.

    Parameters
    ----------
    prices : pd.Series
        Series of historical prices indexed by datetime.
    strategy : Callable[[float], str]
        Function that returns "buy", "sell", or "hold" for a given price.

    Returns
    -------
    pd.Series
        The equity curve resulting from applying the strategy.
    """
    cash = 10000.0
    position = 0
    equity_curve = []

    for price in prices:
        action = strategy(price)
        if action == "buy":
            position += 1
            cash -= price
        elif action == "sell" and position > 0:
            position -= 1
            cash += price
        equity_curve.append(cash + position * price)

    return pd.Series(equity_curve, index=prices.index)


def run_strategies_and_plot_grid(
    prices: pd.Series, strategies: List[Callable[[float], str]], ncols: int = 2
) -> None:
    """Run multiple strategies and display their equity curves in a grid.

    Parameters
    ----------
    prices : pd.Series
        Historical price series.
    strategies : list of callables
        Strategy functions to evaluate.
    ncols : int, optional
        Number of columns in the plot grid, by default 2.
    """
    results = []
    for strat in strategies:
        equity = simulate_historical_trades(prices, strat)
        results.append((strat.__name__, equity))

    nrows = math.ceil(len(results) / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(6 * ncols, 4 * nrows))
    axes = np.atleast_1d(axes).flatten()

    for ax, (name, equity) in zip(axes, results):
        equity.plot(ax=ax)
        ax.set_title(name)
        ax.set_xlabel("Time")
        ax.set_ylabel("Equity")

    # Hide unused axes
    for ax in axes[len(results):]:
        ax.axis("off")

    plt.tight_layout()
    plt.show()

