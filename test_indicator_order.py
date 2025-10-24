"""
Test that indicator order (left vs right) matters for crossover strategies.

This test verifies the critical fix: reversing "GMA crosses KAMA" to "KAMA crosses GMA"
must produce different positions and P&L.
"""
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from indicators_core import precompute_gma_grid, precompute_kama_grid
from backtest_core import (
    run_backtest_edges_nb,
    compute_metrics_from_portfolio,
    create_valid_mask,
    compute_crossover_edges,
)


def test_indicator_order_reversal():
    """Test that reversing indicator order changes results."""
    print("\n" + "=" * 70)
    print("INDICATOR ORDER REVERSAL TEST")
    print("=" * 70)
    print("\nThis test verifies that:")
    print("  'GMA crosses KAMA from above' != 'KAMA crosses GMA from above'")
    print("\nBoth use the same tie rule, warmup, and start policy.\n")

    # Generate synthetic data
    np.random.seed(42)
    n = 500
    prices = 100.0 + np.cumsum(np.random.randn(n) * 0.5)
    prices = np.abs(prices)

    # Test several parameter pairs
    test_pairs = [(20, 25), (30, 35), (15, 40)]
    initial_capital = 10000.0

    all_passed = True

    for gp, kp in test_pairs:
        print(f"\n--- Testing GMA={gp}, KAMA={kp} ---")

        # Compute indicators
        gma = precompute_gma_grid(prices, np.array([gp], dtype=np.int64))[gp]
        kama = precompute_kama_grid(prices, np.array([kp], dtype=np.int64), 2, 30)[kp]
        valid_mask = create_valid_mask(gma, kama)

        # Test 1: GMA crosses KAMA from above (GMA left, KAMA right)
        # This means: buy when GMA goes from >KAMA to <KAMA (crosses down)
        buy_gk = compute_crossover_edges(gma, kama, cross_up=False, tie_rule='strict')
        sell_gk = compute_crossover_edges(gma, kama, cross_up=True, tie_rule='strict')

        port_gk, final_gk, trades_gk, buys_gk, sells_gk = run_backtest_edges_nb(
            prices, buy_gk, sell_gk, initial_capital, 
            start_in_sync=False, valid_mask=valid_mask, fee_rate=0.0
        )

        # Test 2: KAMA crosses GMA from above (KAMA left, GMA right)
        # This means: buy when KAMA goes from >GMA to <GMA (crosses down)
        buy_kg = compute_crossover_edges(kama, gma, cross_up=False, tie_rule='strict')
        sell_kg = compute_crossover_edges(kama, gma, cross_up=True, tie_rule='strict')

        port_kg, final_kg, trades_kg, buys_kg, sells_kg = run_backtest_edges_nb(
            prices, buy_kg, sell_kg, initial_capital,
            start_in_sync=False, valid_mask=valid_mask, fee_rate=0.0
        )

        # Calculate P&L
        pl_gk = (final_gk / initial_capital - 1.0) * 100.0
        pl_kg = (final_kg / initial_capital - 1.0) * 100.0
        diff = abs(pl_gk - pl_kg)

        print(f"\n  GMA crosses KAMA:")
        print(f"    P&L: {pl_gk:.2f}%, Buys: {buys_gk}, Sells: {sells_gk}")
        print(f"\n  KAMA crosses GMA:")
        print(f"    P&L: {pl_kg:.2f}%, Buys: {buys_kg}, Sells: {sells_kg}")
        print(f"\n  Difference: {diff:.2f}%")

        # Check if results differ
        if diff > 0.01:
            print(f"  [PASS] Indicator order matters (different P&L)")
        else:
            print(f"  [FAIL] Indicator order ignored (identical P&L)")
            all_passed = False

        # Additional check: buy/sell counts should differ or swap
        counts_differ = (buys_gk != buys_kg) or (sells_gk != sells_kg)
        if counts_differ:
            print(f"  [PASS] Buy/sell counts differ as expected")
        else:
            print(f"  [WARNING] Buy/sell counts identical (unusual)")

    print("\n" + "=" * 70)
    if all_passed:
        print("ALL TESTS PASSED - Indicator order is correctly parsed!")
    else:
        print("SOME TESTS FAILED - Indicator order may be ignored!")
    print("=" * 70 + "\n")

    return all_passed


if __name__ == "__main__":
    success = test_indicator_order_reversal()
    sys.exit(0 if success else 1)

