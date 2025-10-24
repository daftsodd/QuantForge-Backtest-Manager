"""
Optimized backtest core utilities used by generated strategies.

Provides edge-driven and regime-based backtesting with proper indicator order handling.
All strategies respect validity masks, tie rules, and warmup periods.
"""
from __future__ import annotations

import numpy as np
from numba import njit


@njit(cache=True, fastmath=False)
def run_backtest_edges_nb(
    prices: np.ndarray,
    buy_edges: np.ndarray,
    sell_edges: np.ndarray,
    initial_capital: float,
    start_in_sync: bool = False,
    valid_mask: np.ndarray | None = None,
    fee_rate: float = 0.0,
) -> tuple:
    """Edge-driven backtest: trades only on signal transitions.

    Args:
        prices: close prices (float64)
        buy_edges: boolean array, true when a buy edge occurs
        sell_edges: boolean array, true when a sell edge occurs
        initial_capital: starting cash
        start_in_sync: if True, initialize position at first valid bar; else start flat
        valid_mask: boolean array marking bars where indicators are valid
        fee_rate: trading fee as fraction (0.001 = 0.1%)

    Returns:
        (portfolio_values, final_value, trades_count, buy_count, sell_count)
    """
    n = prices.shape[0]
    port = np.empty(n, dtype=np.float64)

    pos = 0  # 0 flat, 1 long
    cash = initial_capital
    shares = 0.0
    trades = 0
    buy_count = 0
    sell_count = 0

    if valid_mask is None:
        valid_mask = np.ones(n, dtype=np.bool_)

    # Find first valid bar
    first_valid = -1
    for i in range(n):
        if valid_mask[i]:
            first_valid = i
            break

    # Initialize position if start_in_sync
    if start_in_sync and first_valid >= 0 and buy_edges[first_valid]:
        price = prices[first_valid]
        shares = cash / price
        cash = 0.0
        pos = 1

    for i in range(n):
        price = prices[i]
        valid = valid_mask[i]
        buy = buy_edges[i] and valid
        sell = sell_edges[i] and valid

        # Edge-driven: only change position on edges
        if pos == 0 and buy:
            # Buy: go long
            cost = cash
            fee = cost * fee_rate
            shares = (cash - fee) / price
            cash = 0.0
            pos = 1
            trades += 1
            buy_count += 1
        elif pos == 1 and sell:
            # Sell: go flat
            proceeds = shares * price
            fee = proceeds * fee_rate
            cash = proceeds - fee
            shares = 0.0
            pos = 0
            sell_count += 1

        # Record portfolio value
        if pos == 1:
            port[i] = shares * price
        else:
            port[i] = cash

    final_val = port[-1]
    return port, final_val, trades, buy_count, sell_count


@njit(cache=True, fastmath=False)
def run_backtest_edges_long_short_nb(
    prices: np.ndarray,
    long_edges: np.ndarray,
    short_edges: np.ndarray,
    initial_capital: float,
    start_flat: bool = True,
    valid_mask: np.ndarray | None = None,
    fee_rate: float = 0.0,
) -> tuple:
    """Edge-driven long/short backtest: trades on edges, always in market.

    Args:
        prices: close prices
        long_edges: boolean array, True when a long entry edge occurs
        short_edges: boolean array, True when a short entry edge occurs
        initial_capital: starting capital
        start_flat: if True, wait for first edge; if False, start in a position (based on first edge type)
        valid_mask: validity mask
        fee_rate: trading fee as fraction

    Returns:
        (portfolio_values, final_value, transitions, long_bars, short_bars)
    """
    n = prices.shape[0]
    port = np.empty(n, dtype=np.float64)

    pos = 0  # 0 flat, +1 long, -1 short
    cash = initial_capital
    shares = 0.0
    transitions = 0
    long_bars = 0
    short_bars = 0

    if valid_mask is None:
        valid_mask = np.ones(n, dtype=np.bool_)

    # Find first valid edge to initialize if not start_flat
    if not start_flat:
        for i in range(n):
            if valid_mask[i]:
                if long_edges[i]:
                    # Start long
                    shares = cash / prices[i]
                    cash = 0.0
                    pos = 1
                    break
                elif short_edges[i]:
                    # Start short
                    shares = -cash / prices[i]
                    cash = 2 * initial_capital
                    pos = -1
                    break

    for i in range(n):
        price = prices[i]
        valid = valid_mask[i]
        long_sig = long_edges[i] and valid
        short_sig = short_edges[i] and valid

        # Transition on edge signals
        if long_sig and pos != 1:
            # Close current position (if any) and go long
            if pos == -1:
                # Close short
                cost = -shares * price
                cash = cash - cost
                shares = 0.0
                # Apply fee
                fee = abs(cash - initial_capital) * fee_rate
                cash -= fee
            # Go long
            if pos != 1:
                shares = cash / price
                cash = 0.0
                pos = 1
                transitions += 1

        elif short_sig and pos != -1:
            # Close current position (if any) and go short
            if pos == 1:
                # Close long
                proceeds = shares * price
                cash = proceeds
                shares = 0.0
                # Apply fee
                fee = abs(cash - initial_capital) * fee_rate
                cash -= fee
            # Go short
            if pos != -1:
                shares = -cash / price
                cash = 2 * cash
                pos = -1
                transitions += 1

        # Record portfolio value
        if pos == 1:
            port[i] = shares * price
            long_bars += 1
        elif pos == -1:
            port[i] = cash + shares * price
            short_bars += 1
        else:
            port[i] = cash

    final_val = port[-1]
    return port, final_val, transitions, long_bars, short_bars


@njit(cache=True, fastmath=False)
def run_backtest_regime_long_only_nb(
    prices: np.ndarray,
    regime: np.ndarray,
    initial_capital: float,
    valid_mask: np.ndarray | None = None,
    fee_rate: float = 0.0,
) -> tuple:
    """Regime-based backtest: long when regime=True, flat when regime=False.

    Args:
        prices: close prices
        regime: boolean array, True when should be long
        initial_capital: starting cash
        valid_mask: validity mask
        fee_rate: trading fee as fraction

    Returns:
        (portfolio_values, final_value, trades_count, long_bars, flat_bars)
    """
    n = prices.shape[0]
    port = np.empty(n, dtype=np.float64)

    pos = 0  # 0 flat, 1 long
    cash = initial_capital
    shares = 0.0
    trades = 0
    long_bars = 0
    flat_bars = 0

    if valid_mask is None:
        valid_mask = np.ones(n, dtype=np.bool_)

    for i in range(n):
        price = prices[i]
        valid = valid_mask[i]
        target = regime[i] and valid

        # Transition on regime change
        if pos == 0 and target:
            # Enter long
            cost = cash
            fee = cost * fee_rate
            shares = (cash - fee) / price
            cash = 0.0
            pos = 1
            trades += 1
        elif pos == 1 and not target:
            # Exit to flat
            proceeds = shares * price
            fee = proceeds * fee_rate
            cash = proceeds - fee
            shares = 0.0
            pos = 0

        # Record portfolio value
        if pos == 1:
            port[i] = shares * price
            long_bars += 1
        else:
            port[i] = cash
            flat_bars += 1

    final_val = port[-1]
    return port, final_val, trades, long_bars, flat_bars


@njit(cache=True, fastmath=False)
def run_backtest_regime_long_short_nb(
    prices: np.ndarray,
    regime: np.ndarray,
    initial_capital: float,
    valid_mask: np.ndarray | None = None,
    fee_rate: float = 0.0,
) -> tuple:
    """Regime-based backtest: long when regime=True, short when regime=False.

    Args:
        prices: close prices
        regime: boolean array, True=long, False=short
        initial_capital: starting cash
        valid_mask: validity mask
        fee_rate: trading fee as fraction

    Returns:
        (portfolio_values, final_value, transitions_count, long_bars, short_bars)
    """
    n = prices.shape[0]
    port = np.empty(n, dtype=np.float64)

    pos = 0  # +1 long, -1 short
    cash = initial_capital
    shares = 0.0
    transitions = 0
    long_bars = 0
    short_bars = 0

    if valid_mask is None:
        valid_mask = np.ones(n, dtype=np.bool_)

    # Find first valid bar to initialize
    first_valid = -1
    for i in range(n):
        if valid_mask[i]:
            first_valid = i
            break

    if first_valid >= 0:
        # Initialize to regime at first valid bar
        price = prices[first_valid]
        if regime[first_valid]:
            # Start long
            shares = cash / price
            cash = 0.0
            pos = 1
        else:
            # Start short
            shares = -cash / price
            cash = 2 * initial_capital  # cash from short sale
            pos = -1

    for i in range(n):
        price = prices[i]
        valid = valid_mask[i]
        target = 1 if (regime[i] and valid) else -1

        # Transition on regime flip
        if pos != 0 and pos != target:
            # Close current position
            if pos == 1:
                # Close long
                proceeds = shares * price
                cash = proceeds
                shares = 0.0
            else:
                # Close short
                cost = -shares * price
                cash = cash - cost
                shares = 0.0

            # Apply fee on transition
            fee = abs(cash - initial_capital) * fee_rate
            cash -= fee

            # Open new position
            if target == 1:
                # Go long
                shares = cash / price
                cash = 0.0
            else:
                # Go short
                shares = -cash / price
                cash = 2 * cash

            pos = target
            transitions += 1

        # Record portfolio value
        if pos == 1:
            port[i] = shares * price
            long_bars += 1
        else:
            # Short: portfolio = cash - (shares * price)
            port[i] = cash + shares * price
            short_bars += 1

    final_val = port[-1]
    return port, final_val, transitions, long_bars, short_bars


def compute_metrics_from_portfolio(
    port: np.ndarray,
    initial_capital: float,
    periods_per_year: int = 365,
) -> dict:
    """Compute metrics with correct annualization.

    Args:
        port: portfolio value array
        initial_capital: starting capital
        periods_per_year: number of bars per year (365 for daily, 252 for trading days, etc.)

    Returns:
        dict of metrics
    """
    n = port.shape[0]
    ret = np.empty(n, dtype=np.float64)
    ret[0] = 0.0
    for i in range(1, n):
        prev = port[i - 1]
        ret[i] = (port[i] / prev) - 1.0
    total_prof = (port[-1] / initial_capital - 1.0) * 100.0

    # Sharpe: annualized
    std = ret.std(ddof=1)
    sharpe = (ret.mean() / std * np.sqrt(float(periods_per_year))) if std != 0.0 else 0.0

    # Sortino: annualized
    neg = ret[ret < 0.0]
    if neg.size > 0:
        neg_std = neg.std(ddof=1)
    else:
        neg_std = 0.0
    sortino = (
        (ret.mean() * periods_per_year) / (neg_std * np.sqrt(float(periods_per_year)))
        if neg.size > 0 and neg_std != 0.0
        else 0.0
    )

    # Omega
    pos_sum = ret[ret > 0.0].sum()
    neg_sum = ret[ret < 0.0].sum()
    omega = pos_sum / abs(neg_sum) if neg_sum != 0.0 else float("inf")

    # Max Drawdown: peak-to-trough
    cummax = np.maximum.accumulate(port)
    dd = (port - cummax) / cummax
    drawdown = abs(dd.min() * 100.0)

    return {
        "Sharpe_Ratio": sharpe,
        "Sortino_Ratio": sortino,
        "Omega_Ratio": omega,
        "Max_Drawdown_%": drawdown,
        "Total_Profit_%": total_prof,
        "Final_Portfolio_Value": port[-1],
    }


def create_valid_mask(ind1: np.ndarray, ind2: np.ndarray) -> np.ndarray:
    """Create validity mask: True where both indicators are non-NaN."""
    return (~np.isnan(ind1)) & (~np.isnan(ind2))


def compute_crossover_edges(
    left: np.ndarray,
    right: np.ndarray,
    cross_up: bool = True,
    tie_rule: str = "strict",
) -> np.ndarray:
    """Compute true crossover edges (previous vs current comparison).

    Args:
        left: left indicator array
        right: right indicator array
        cross_up: if True, detect left crossing right from below (buy edge)
                  if False, detect left crossing right from above (sell edge)
        tie_rule: "strict" (default) uses < and >, "inclusive" uses <= and >=

    Returns:
        boolean array of crossover events
    """
    n = left.shape[0]
    signal = np.zeros(n, dtype=np.bool_)
    prev_left = np.empty(n, dtype=np.float64)
    prev_right = np.empty(n, dtype=np.float64)
    prev_left[0] = np.nan
    prev_right[0] = np.nan
    prev_left[1:] = left[:-1]
    prev_right[1:] = right[:-1]

    if tie_rule == "strict":
        if cross_up:
            # Left crosses right from below: prev_left < prev_right AND left > right
            signal = (prev_left < prev_right) & (left > right)
        else:
            # Left crosses right from above: prev_left > prev_right AND left < right
            signal = (prev_left > prev_right) & (left < right)
    else:  # inclusive
        if cross_up:
            signal = (prev_left <= prev_right) & (left >= right)
        else:
            signal = (prev_left >= prev_right) & (left <= right)

    return signal


def compute_regime(
    left: np.ndarray,
    right: np.ndarray,
    greater_than: bool = True,
    tie_rule: str = "strict",
) -> np.ndarray:
    """Compute regime array for > or < strategies.

    Args:
        left: left indicator
        right: right indicator
        greater_than: if True, regime=True when left>right; else left<right
        tie_rule: "strict" or "hold_prior" (on equality, keep previous state)

    Returns:
        boolean regime array
    """
    n = left.shape[0]
    regime = np.zeros(n, dtype=np.bool_)

    if tie_rule == "strict":
        if greater_than:
            regime = left > right
        else:
            regime = left < right
    else:  # hold_prior
        # On equality, maintain previous state
        for i in range(n):
            if i == 0:
                if greater_than:
                    regime[i] = left[i] > right[i]
                else:
                    regime[i] = left[i] < right[i]
            else:
                if left[i] == right[i]:
                    regime[i] = regime[i - 1]
                else:
                    if greater_than:
                        regime[i] = left[i] > right[i]
                    else:
                        regime[i] = left[i] < right[i]

    return regime


def diagnostic_first_events(
    signal1: np.ndarray,
    signal2: np.ndarray,
    valid_mask: np.ndarray,
    max_events: int = 5,
) -> dict:
    """Return indices of first few signal events for debugging."""
    idx1 = np.where(signal1 & valid_mask)[0]
    idx2 = np.where(signal2 & valid_mask)[0]
    first_valid = np.where(valid_mask)[0]
    return {
        "signal1_indices": idx1[:max_events].tolist() if idx1.size > 0 else [],
        "signal2_indices": idx2[:max_events].tolist() if idx2.size > 0 else [],
        "first_valid_index": int(first_valid[0]) if first_valid.size > 0 else -1,
        "total_signal1": int(idx1.size),
        "total_signal2": int(idx2.size),
    }
