"""
Optimized, reusable indicator implementations for QuantForge.

Contains Numba-accelerated KAMA and fast GMA implementations,
including helpers to precompute indicator grids across many periods
for parameter sweeps.
"""
from __future__ import annotations

import numpy as np
from numba import njit


@njit(cache=True, fastmath=False)
def _gma_from_log_nb(log_prices: np.ndarray, window: int) -> np.ndarray:
    """Compute Geometric Moving Average (GMA) for one window using cumulative sums of logs.

    GMA_t = exp( mean( log(price[t-window+1:t]) ) ) with min_periods = window
    For t < window-1, the value is NaN to match pandas behavior here (caller may decide).
    """
    n = log_prices.shape[0]
    out = np.empty(n, dtype=np.float64)
    out[:] = np.nan
    if window < 1:
        return out

    csum = np.empty(n + 1, dtype=np.float64)
    csum[0] = 0.0
    for i in range(n):
        csum[i + 1] = csum[i] + log_prices[i]

    w = window
    for t in range(w - 1, n):
        s = csum[t + 1] - csum[t + 1 - w]
        out[t] = np.exp(s / w)
    return out


def precompute_gma_grid(close: np.ndarray, periods: np.ndarray) -> dict:
    """Precompute GMA arrays for all periods.

    Args:
        close: float64 array of close prices.
        periods: array of integer window sizes.
    Returns:
        dict mapping period -> float64 array of GMA values.
    """
    log_prices = np.log(close.astype(np.float64))
    periods = np.asarray(periods, dtype=np.int64)
    grid = {}
    for p in periods:
        grid[int(p)] = _gma_from_log_nb(log_prices, int(p))
    return grid


@njit(cache=True, fastmath=False)
def _kama_nb(prices: np.ndarray, window: int, fast_period: int, slow_period: int) -> np.ndarray:
    """Compute Kaufman Adaptive Moving Average for one window.

    Matches pandas reference implementation used in the app:
    change = abs(price[t] - price[t-window])
    volatility = rolling_sum(abs(diff(price)), window)
    er = change / volatility (NaN or 0 -> 0)
    sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
    kama[:window] = price[:window]
    for t >= window: kama[t] = kama[t-1] + sc[t] * (price[t] - kama[t-1])
    """
    n = prices.shape[0]
    out = np.empty(n, dtype=np.float64)
    if window < 1:
        # Degenerate: just copy prices
        for i in range(n):
            out[i] = prices[i]
        return out

    # Precompute abs diff and its cumsum for rolling volatility
    abs_diff = np.empty(n, dtype=np.float64)
    abs_diff[0] = np.nan
    for i in range(1, n):
        d = prices[i] - prices[i - 1]
        if d < 0:
            d = -d
        abs_diff[i] = d

    csum = np.empty(n + 1, dtype=np.float64)
    csum[0] = 0.0
    for i in range(n):
        # Treat NaN as 0 in cumulative sum so that windows < window remain NaN by index check below
        v = abs_diff[i]
        if not (v == v):  # NaN check
            v = 0.0
        csum[i + 1] = csum[i] + v

    fast_sc = 2.0 / (fast_period + 1.0)
    slow_sc = 2.0 / (slow_period + 1.0)

    # Initialize first window as price to match reference
    for i in range(n):
        if i < window:
            out[i] = prices[i]
        else:
            break

    for t in range(window, n):
        # change over window
        ch = prices[t] - prices[t - window]
        if ch < 0:
            ch = -ch

        # rolling volatility over last 'window' diffs: sum(abs_diff[t-window+1 .. t])
        start = t - window + 1
        vol = csum[t + 1] - csum[start]

        # efficiency ratio
        er = 0.0
        if vol != 0.0 and vol == vol:  # not NaN
            er = ch / vol

        sc = er * (fast_sc - slow_sc) + slow_sc
        sc = sc * sc
        prev = out[t - 1]
        out[t] = prev + sc * (prices[t] - prev)

    return out


def precompute_kama_grid(close: np.ndarray, periods: np.ndarray, fast_period: int, slow_period: int) -> dict:
    """Precompute KAMA arrays for all periods.

    Args:
        close: float64 array of close prices.
        periods: array of integer window sizes.
        fast_period: KAMA fast period (ER upper bound smoothing)
        slow_period: KAMA slow period (ER lower bound smoothing)
    Returns:
        dict mapping period -> float64 array of KAMA values.
    """
    prices = close.astype(np.float64)
    periods = np.asarray(periods, dtype=np.int64)
    grid = {}
    for p in periods:
        grid[int(p)] = _kama_nb(prices, int(p), int(fast_period), int(slow_period))
    return grid


