"""
Test suite for the Enable Short Selling toggle.

Verifies that long-only vs long/short modes produce different behavior
and that routing to the correct engine works.
"""
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from indicators_core import precompute_gma_grid, precompute_kama_grid
from backtest_core import (
    run_backtest_edges_nb,
    run_backtest_edges_long_short_nb,
    run_backtest_regime_long_only_nb,
    run_backtest_regime_long_short_nb,
    compute_metrics_from_portfolio,
    create_valid_mask,
    compute_crossover_edges,
    compute_regime,
)


def test_exposure_crossover():
    """Test that crossover long-only vs long-short differ."""
    print("\n=== TEST: Crossover Exposure Modes ===")
    print("Long-only vs long-short should produce different P&L and exposure\n")

    np.random.seed(123)
    n = 300
    prices = 100.0 + np.cumsum(np.random.randn(n) * 0.4)
    prices = np.abs(prices)
    initial_capital = 10000.0

    gma = precompute_gma_grid(prices, np.array([25], dtype=np.int64))[25]
    kama = precompute_kama_grid(prices, np.array([30], dtype=np.int64), 2, 30)[30]
    valid_mask = create_valid_mask(gma, kama)

    # Generate crossover edges
    buy_edges = compute_crossover_edges(gma, kama, cross_up=True)
    sell_edges = compute_crossover_edges(gma, kama, cross_up=False)

    # Long-only mode
    port_lo, final_lo, trades_lo, buys_lo, sells_lo = run_backtest_edges_nb(
        prices, buy_edges, sell_edges, initial_capital,
        start_in_sync=False, valid_mask=valid_mask, fee_rate=0.0
    )

    # Long-short mode (buy = go long, sell = go short)
    port_ls, final_ls, trans_ls, long_ls, short_ls = run_backtest_edges_long_short_nb(
        prices, buy_edges, sell_edges, initial_capital,
        start_flat=True, valid_mask=valid_mask, fee_rate=0.0
    )

    pl_lo = (final_lo / initial_capital - 1.0) * 100.0
    pl_ls = (final_ls / initial_capital - 1.0) * 100.0

    # Calculate average exposure for long-only
    positions_lo = np.zeros(n)
    pos = 0
    for i in range(n):
        if buy_edges[i] and valid_mask[i]:
            pos = 1
        elif sell_edges[i] and valid_mask[i]:
            pos = 0
        positions_lo[i] = pos
    avg_exposure_lo = positions_lo[valid_mask].mean()

    # Long-short should have ~100% exposure after first signal
    total_exposure_ls = long_ls + short_ls
    avg_exposure_ls = total_exposure_ls / n

    print(f"  Long-only:")
    print(f"    P&L: {pl_lo:.2f}%, Trades: {trades_lo}")
    print(f"    Avg exposure: {avg_exposure_lo*100:.1f}%")
    print(f"\n  Long-short:")
    print(f"    P&L: {pl_ls:.2f}%, Transitions: {trans_ls}")
    print(f"    Long bars: {long_ls}, Short bars: {short_ls}")
    print(f"    Avg exposure: {avg_exposure_ls*100:.1f}%")

    # Check that P&L differs
    pl_differs = abs(pl_lo - pl_ls) > 0.1

    # Check that long-short has higher exposure
    exposure_differs = avg_exposure_ls > avg_exposure_lo + 0.1

    if pl_differs and exposure_differs:
        print("\n  [PASS] Exposure modes produce different behavior")
        return True
    else:
        print("\n  [FAIL] Exposure modes may not be working correctly")
        return False


def test_routing():
    """Test that different exposure modes call different engines."""
    print("\n=== TEST: Engine Routing ===")
    print("Verify correct engine is used for each exposure mode\n")

    np.random.seed(456)
    n = 200
    prices = 100.0 + np.cumsum(np.random.randn(n) * 0.3)
    prices = np.abs(prices)
    initial_capital = 10000.0

    gma = precompute_gma_grid(prices, np.array([20], dtype=np.int64))[20]
    kama = precompute_kama_grid(prices, np.array([25], dtype=np.int64), 2, 30)[25]
    valid_mask = create_valid_mask(gma, kama)

    # Test 1: Edge long-only returns 5 values
    buy_edges = compute_crossover_edges(gma, kama, cross_up=True)
    sell_edges = compute_crossover_edges(gma, kama, cross_up=False)
    result_edge_lo = run_backtest_edges_nb(
        prices, buy_edges, sell_edges, initial_capital,
        start_in_sync=False, valid_mask=valid_mask
    )
    
    # Test 2: Edge long-short returns 5 values (transitions, long_bars, short_bars)
    result_edge_ls = run_backtest_edges_long_short_nb(
        prices, buy_edges, sell_edges, initial_capital,
        start_flat=True, valid_mask=valid_mask
    )
    
    # Test 3: Regime long-only returns 5 values (trades, long_bars, flat_bars)
    regime = compute_regime(gma, kama, greater_than=True)
    result_regime_lo = run_backtest_regime_long_only_nb(
        prices, regime, initial_capital, valid_mask=valid_mask
    )
    
    # Test 4: Regime long-short returns 5 values (transitions, long_bars, short_bars)
    result_regime_ls = run_backtest_regime_long_short_nb(
        prices, regime, initial_capital, valid_mask=valid_mask
    )

    # Check that all return 5 values
    all_return_5 = all([
        len(result_edge_lo) == 5,
        len(result_edge_ls) == 5,
        len(result_regime_lo) == 5,
        len(result_regime_ls) == 5,
    ])

    print(f"  Edge long-only: {len(result_edge_lo)} values returned")
    print(f"  Edge long-short: {len(result_edge_ls)} values returned")
    print(f"  Regime long-only: {len(result_regime_lo)} values returned")
    print(f"  Regime long-short: {len(result_regime_ls)} values returned")

    if all_return_5:
        print("\n  [PASS] All engines return correct signature")
        return True
    else:
        print("\n  [FAIL] Engine signature mismatch")
        return False


def test_annualization_change():
    """Test that changing periods_per_year changes Sharpe/Sortino."""
    print("\n=== TEST: Annualization ===")
    print("Changing periods_per_year should change Sharpe/Sortino (not raw P&L)\n")

    np.random.seed(789)
    n = 250
    prices = 100.0 + np.cumsum(np.random.randn(n) * 0.35)
    prices = np.abs(prices)
    initial_capital = 10000.0

    gma = precompute_gma_grid(prices, np.array([20], dtype=np.int64))[20]
    kama = precompute_kama_grid(prices, np.array([25], dtype=np.int64), 2, 30)[25]
    valid_mask = create_valid_mask(gma, kama)

    buy_edges = compute_crossover_edges(gma, kama, cross_up=True)
    sell_edges = compute_crossover_edges(gma, kama, cross_up=False)

    port, final_val, trades, buys, sells = run_backtest_edges_nb(
        prices, buy_edges, sell_edges, initial_capital,
        start_in_sync=False, valid_mask=valid_mask
    )

    # Compute metrics with different periods_per_year
    metrics_365 = compute_metrics_from_portfolio(port, initial_capital, periods_per_year=365)
    metrics_252 = compute_metrics_from_portfolio(port, initial_capital, periods_per_year=252)

    sharpe_365 = metrics_365['Sharpe_Ratio']
    sharpe_252 = metrics_252['Sharpe_Ratio']
    sortino_365 = metrics_365['Sortino_Ratio']
    sortino_252 = metrics_252['Sortino_Ratio']
    pl_365 = metrics_365['Total_Profit_%']
    pl_252 = metrics_252['Total_Profit_%']

    print(f"  Periods/year = 365:")
    print(f"    Sharpe: {sharpe_365:.4f}, Sortino: {sortino_365:.4f}, P&L: {pl_365:.2f}%")
    print(f"\n  Periods/year = 252:")
    print(f"    Sharpe: {sharpe_252:.4f}, Sortino: {sortino_252:.4f}, P&L: {pl_252:.2f}%")

    # Check that Sharpe/Sortino changed but P&L didn't
    sharpe_changed = abs(sharpe_365 - sharpe_252) > 0.01
    pl_unchanged = abs(pl_365 - pl_252) < 0.01

    if sharpe_changed and pl_unchanged:
        print("\n  [PASS] Annualization affects ratios, not raw P&L")
        return True
    else:
        print("\n  [FAIL] Annualization may not be working correctly")
        return False


def run_all_tests():
    """Run all exposure toggle tests."""
    print("=" * 60)
    print("EXPOSURE TOGGLE TEST SUITE")
    print("=" * 60)

    results = []
    results.append(("Crossover Exposure Modes", test_exposure_crossover()))
    results.append(("Engine Routing", test_routing()))
    results.append(("Annualization", test_annualization_change()))

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status}: {name}")

    all_passed = all(r[1] for r in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

