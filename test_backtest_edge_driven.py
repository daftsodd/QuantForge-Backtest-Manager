"""
Test harness for edge-driven backtest semantics.

Acceptance criteria:
1. Reversal test: reversing crossover definition changes positions and P&L
2. Hold-all sanity: always-long matches buy-and-hold
3. Determinism: same inputs yield identical outputs
4. Warmup: no trades before both indicators are valid
"""
import numpy as np
import sys
import os

# Add parent to path to import cores
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from indicators_core import precompute_gma_grid, precompute_kama_grid
from backtest_core import (
    run_backtest_edges_nb,
    run_backtest_regime_long_only_nb,
    run_backtest_regime_long_short_nb,
    compute_metrics_from_portfolio,
    create_valid_mask,
    compute_crossover_edges,
    compute_regime,
    diagnostic_first_events,
)


def test_reversal():
    """Test that reversing crossover definition changes results."""
    print("\n=== TEST 1: Reversal Test ===")
    print("Reversing 'GMA crosses KAMA from above' <-> 'from below' must change P&L\n")

    # Generate synthetic price data
    np.random.seed(42)
    n = 500
    prices = 100.0 + np.cumsum(np.random.randn(n) * 0.5)
    prices = np.abs(prices)  # ensure positive

    # Compute indicators for a few parameter pairs
    gma_periods = [20, 30]
    kama_periods = [25, 35]
    initial_capital = 10000.0

    gma_grid = precompute_gma_grid(prices, np.array(gma_periods, dtype=np.int64))
    kama_grid = precompute_kama_grid(prices, np.array(kama_periods, dtype=np.int64), fast_period=2, slow_period=30)

    results = []
    for gp in gma_periods:
        for kp in kama_periods:
            gma = gma_grid[gp]
            kama = kama_grid[kp]
            valid_mask = create_valid_mask(gma, kama)

            # Definition A: GMA crosses KAMA from above (buy when GMA > KAMA after being below)
            buy_A = compute_crossover_edges(gma, kama, cross_up=True)
            sell_A = compute_crossover_edges(gma, kama, cross_up=False)

            # Definition B: reversed (GMA crosses KAMA from below)
            buy_B = compute_crossover_edges(gma, kama, cross_up=False)
            sell_B = compute_crossover_edges(gma, kama, cross_up=True)

            # Run backtests
            port_A, final_A, trades_A, buys_A, sells_A = run_backtest_edges_nb(
                prices, buy_A, sell_A, initial_capital, start_in_sync=False, valid_mask=valid_mask
            )
            port_B, final_B, trades_B, buys_B, sells_B = run_backtest_edges_nb(
                prices, buy_B, sell_B, initial_capital, start_in_sync=False, valid_mask=valid_mask
            )

            # Check if results differ
            pl_A = (final_A / initial_capital - 1.0) * 100.0
            pl_B = (final_B / initial_capital - 1.0) * 100.0
            diff = abs(pl_A - pl_B)

            results.append({
                'gma': gp,
                'kama': kp,
                'pl_A': pl_A,
                'pl_B': pl_B,
                'diff': diff,
                'buys_A': buys_A,
                'sells_A': sells_A,
                'buys_B': buys_B,
                'sells_B': sells_B,
            })

            print(f"  GMA={gp}, KAMA={kp}:")
            print(f"    Definition A: P&L={pl_A:.2f}%, Buys={buys_A}, Sells={sells_A}")
            print(f"    Definition B: P&L={pl_B:.2f}%, Buys={buys_B}, Sells={sells_B}")
            print(f"    Difference: {diff:.2f}%")

    # Check acceptance: at least one pair should have different P&L
    any_different = any(r['diff'] > 0.01 for r in results)
    if any_different:
        print("\n  [PASS] Reversal changes results (as expected)")
        return True
    else:
        print("\n  [FAIL] Reversal produces identical results (BUG: not edge-driven)")
        return False


def test_hold_all():
    """Test that always-long matches buy-and-hold."""
    print("\n=== TEST 2: Hold-All Sanity ===")
    print("Always-long should match buy-and-hold (no fees)\n")

    np.random.seed(123)
    n = 300
    prices = 100.0 + np.cumsum(np.random.randn(n) * 0.3)
    prices = np.abs(prices)
    initial_capital = 10000.0

    # Create always-long signals: buy at first bar, never sell
    buy_signal = np.zeros(n, dtype=np.bool_)
    buy_signal[0] = True
    sell_signal = np.zeros(n, dtype=np.bool_)
    valid_mask = np.ones(n, dtype=np.bool_)

    port, final_val, trades, buys, sells = run_backtest_edges_nb(
        prices, buy_signal, sell_signal, initial_capital, start_in_sync=False, valid_mask=valid_mask
    )

    # Expected: buy-and-hold return
    expected_final = initial_capital * (prices[-1] / prices[0])
    actual_final = final_val
    error = abs(expected_final - actual_final) / expected_final * 100.0

    print(f"  Expected final value: ${expected_final:.2f}")
    print(f"  Actual final value:   ${actual_final:.2f}")
    print(f"  Error: {error:.4f}%")
    print(f"  Trades: {trades}, Buys: {buys}, Sells: {sells}")

    if error < 0.01:
        print("\n  [PASS] Hold-all matches buy-and-hold")
        return True
    else:
        print("\n  [FAIL] Hold-all does not match buy-and-hold")
        return False


def test_determinism():
    """Test that running twice yields identical results."""
    print("\n=== TEST 3: Determinism ===")
    print("Running same backtest twice should yield identical results\n")

    np.random.seed(999)
    n = 200
    prices = 100.0 + np.cumsum(np.random.randn(n) * 0.4)
    prices = np.abs(prices)
    initial_capital = 10000.0

    gma = precompute_gma_grid(prices, np.array([25], dtype=np.int64))[25]
    kama = precompute_kama_grid(prices, np.array([30], dtype=np.int64), fast_period=2, slow_period=30)[30]
    valid_mask = create_valid_mask(gma, kama)

    buy_signal = compute_crossover_edges(gma, kama, cross_up=True)
    sell_signal = compute_crossover_edges(gma, kama, cross_up=False)

    # Run twice
    port1, final1, trades1, buys1, sells1 = run_backtest_edges_nb(
        prices, buy_signal, sell_signal, initial_capital, start_in_sync=False, valid_mask=valid_mask
    )
    port2, final2, trades2, buys2, sells2 = run_backtest_edges_nb(
        prices, buy_signal, sell_signal, initial_capital, start_in_sync=False, valid_mask=valid_mask
    )

    identical = (final1 == final2) and (trades1 == trades2) and np.array_equal(port1, port2)

    print(f"  Run 1: Final=${final1:.2f}, Trades={trades1}")
    print(f"  Run 2: Final=${final2:.2f}, Trades={trades2}")
    print(f"  Identical: {identical}")

    if identical:
        print("\n  [PASS] Determinism verified")
        return True
    else:
        print("\n  [FAIL] Results differ between runs")
        return False


def test_warmup():
    """Test that no trades occur before indicators are valid."""
    print("\n=== TEST 4: Warmup / Validity Gating ===")
    print("No trades should occur before both indicators are valid\n")

    np.random.seed(777)
    n = 400
    prices = 100.0 + np.cumsum(np.random.randn(n) * 0.5)
    prices = np.abs(prices)
    initial_capital = 10000.0

    gma_period = 50
    kama_period = 60
    gma = precompute_gma_grid(prices, np.array([gma_period], dtype=np.int64))[gma_period]
    kama = precompute_kama_grid(prices, np.array([kama_period], dtype=np.int64), fast_period=2, slow_period=30)[kama_period]
    valid_mask = create_valid_mask(gma, kama)

    buy_signal = compute_crossover_edges(gma, kama, cross_up=True)
    sell_signal = compute_crossover_edges(gma, kama, cross_up=False)

    # Get diagnostics
    diag = diagnostic_first_events(buy_signal, sell_signal, valid_mask, max_events=5)
    first_valid = diag['first_valid_index']
    first_buy = diag['signal1_indices'][0] if diag['signal1_indices'] else -1
    first_sell = diag['signal2_indices'][0] if diag['signal2_indices'] else -1

    print(f"  First valid bar: {first_valid}")
    print(f"  First buy event: {first_buy}")
    print(f"  First sell event: {first_sell}")
    print(f"  Total buys: {diag['total_signal1']}, Total sells: {diag['total_signal2']}")

    # Check that first trade is not before first valid
    warmup_ok = True
    if first_buy >= 0 and first_buy < first_valid:
        print(f"  [FAIL] Buy at index {first_buy} before first valid {first_valid}")
        warmup_ok = False
    if first_sell >= 0 and first_sell < first_valid:
        print(f"  [FAIL] Sell at index {first_sell} before first valid {first_valid}")
        warmup_ok = False

    if warmup_ok:
        print("\n  [PASS] No trades before warmup")
        return True
    else:
        return False


def test_grid_indexing():
    """Test that grid indexing is correct (period N stored at key N)."""
    print("\n=== TEST 5: Grid Indexing Sanity ===")
    print("Verify that period N is stored at grid[N] and computes correctly\n")

    np.random.seed(555)
    n = 100
    prices = 100.0 + np.cumsum(np.random.randn(n) * 0.3)
    prices = np.abs(prices)

    # Test GMA for period 10
    period = 10
    gma_grid = precompute_gma_grid(prices, np.array([period], dtype=np.int64))
    gma = gma_grid[period]

    # Manual check: GMA at index period-1 should be exp(mean(log(prices[0:period])))
    # Actually, GMA with min_periods=period means first valid value is at index period-1
    first_valid_idx = period - 1
    expected_gma = np.exp(np.mean(np.log(prices[:period])))
    actual_gma = gma[first_valid_idx]

    error = abs(expected_gma - actual_gma) / expected_gma * 100.0

    print(f"  Period: {period}")
    print(f"  First valid index: {first_valid_idx}")
    print(f"  Expected GMA[{first_valid_idx}]: {expected_gma:.4f}")
    print(f"  Actual GMA[{first_valid_idx}]:   {actual_gma:.4f}")
    print(f"  Error: {error:.4f}%")

    if error < 0.01:
        print("\n  [PASS] Grid indexing correct")
        return True
    else:
        print("\n  [FAIL] Grid indexing mismatch")
        return False


def test_regime_long_only():
    """Test regime long-only strategy."""
    print("\n=== TEST 6: Regime Long-Only ===")
    print("Test that regime transitions produce trades\n")

    np.random.seed(888)
    n = 200
    prices = 100.0 + np.cumsum(np.random.randn(n) * 0.4)
    prices = np.abs(prices)
    initial_capital = 10000.0

    gma = precompute_gma_grid(prices, np.array([20], dtype=np.int64))[20]
    kama = precompute_kama_grid(prices, np.array([25], dtype=np.int64), 2, 30)[25]
    valid_mask = create_valid_mask(gma, kama)

    # Test: regime where GMA > KAMA
    regime_gt = compute_regime(gma, kama, greater_than=True, tie_rule='strict')
    port_gt, final_gt, trades_gt, long_gt, flat_gt = run_backtest_regime_long_only_nb(
        prices, regime_gt, initial_capital, valid_mask, fee_rate=0.0
    )

    # Test: flipped regime (GMA < KAMA)
    regime_lt = compute_regime(gma, kama, greater_than=False, tie_rule='strict')
    port_lt, final_lt, trades_lt, long_lt, flat_lt = run_backtest_regime_long_only_nb(
        prices, regime_lt, initial_capital, valid_mask, fee_rate=0.0
    )

    pl_gt = (final_gt / initial_capital - 1.0) * 100.0
    pl_lt = (final_lt / initial_capital - 1.0) * 100.0

    print(f"  GMA > KAMA regime:")
    print(f"    P&L: {pl_gt:.2f}%, Trades: {trades_gt}, Long bars: {long_gt}, Flat bars: {flat_gt}")
    print(f"\n  GMA < KAMA regime:")
    print(f"    P&L: {pl_lt:.2f}%, Trades: {trades_lt}, Long bars: {long_lt}, Flat bars: {flat_lt}")

    # Check that trades occurred and P&L differs
    trades_ok = (trades_gt > 0) and (trades_lt > 0)
    pl_differs = abs(pl_gt - pl_lt) > 0.01

    if trades_ok and pl_differs:
        print("\n  [PASS] Regime long-only works correctly")
        return True
    else:
        print("\n  [FAIL] Regime long-only issue detected")
        return False


def test_regime_long_short():
    """Test regime long-short strategy."""
    print("\n=== TEST 7: Regime Long-Short ===")
    print("Test that long/short flips incur costs and maintains exposure\n")

    np.random.seed(999)
    n = 150
    prices = 100.0 + np.cumsum(np.random.randn(n) * 0.3)
    prices = np.abs(prices)
    initial_capital = 10000.0

    gma = precompute_gma_grid(prices, np.array([15], dtype=np.int64))[15]
    kama = precompute_kama_grid(prices, np.array([20], dtype=np.int64), 2, 30)[20]
    valid_mask = create_valid_mask(gma, kama)

    regime = compute_regime(gma, kama, greater_than=True, tie_rule='strict')

    # Without fees
    port_no_fee, final_no_fee, trans_no_fee, long_no_fee, short_no_fee = run_backtest_regime_long_short_nb(
        prices, regime, initial_capital, valid_mask, fee_rate=0.0
    )

    # With fees
    port_with_fee, final_with_fee, trans_with_fee, long_with_fee, short_with_fee = run_backtest_regime_long_short_nb(
        prices, regime, initial_capital, valid_mask, fee_rate=0.001
    )

    pl_no_fee = (final_no_fee / initial_capital - 1.0) * 100.0
    pl_with_fee = (final_with_fee / initial_capital - 1.0) * 100.0
    fee_impact = pl_no_fee - pl_with_fee

    print(f"  No fees: P&L={pl_no_fee:.2f}%, Transitions={trans_no_fee}")
    print(f"  With fees (0.1%): P&L={pl_with_fee:.2f}%, Transitions={trans_with_fee}")
    print(f"  Fee impact: {fee_impact:.2f}%")
    print(f"  Exposure: {long_no_fee} long bars, {short_no_fee} short bars")

    # Check that exposure is full (long + short = total bars)
    total_bars = long_no_fee + short_no_fee
    exposure_full = (total_bars == n) or (total_bars >= n - 20)  # Allow some warmup

    # Check that fees reduce P&L
    fee_impact_ok = fee_impact > 0 if trans_no_fee > 0 else True

    if exposure_full and fee_impact_ok:
        print("\n  [PASS] Regime long-short works correctly")
        return True
    else:
        print("\n  [FAIL] Regime long-short issue detected")
        return False


def run_all_tests():
    """Run all acceptance tests."""
    print("=" * 60)
    print("EDGE-DRIVEN BACKTEST TEST SUITE")
    print("=" * 60)

    results = []
    results.append(("Reversal Test", test_reversal()))
    results.append(("Hold-All Sanity", test_hold_all()))
    results.append(("Determinism", test_determinism()))
    results.append(("Warmup Gating", test_warmup()))
    results.append(("Grid Indexing", test_grid_indexing()))
    results.append(("Regime Long-Only", test_regime_long_only()))
    results.append(("Regime Long-Short", test_regime_long_short()))

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

