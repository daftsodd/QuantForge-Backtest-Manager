# Edge-Driven Backtest Implementation

## Summary

The backtest engine has been rewritten to be **edge-driven**: it only trades when buy/sell signals transition from False to True (edges), not based on regime checks. This fixes the bug where reversing crossover definitions produced identical P&L.

## Key Changes

### 1. Edge-Driven Semantics (`backtest_core.py`)

**Before (regime-based):**
- Engine would check `if GMA > KAMA` on every bar and sync position
- Reversing "GMA crosses KAMA from above" ↔ "from below" had no effect

**After (edge-driven):**
- Engine only changes position when `buy_signal[i]` or `sell_signal[i]` is True
- Signals are computed as strict crossover edges: `(prev_ind1 < prev_ind2) & (ind1 > ind2)`
- Ties (`ind1 == ind2`) do not trigger trades
- Reversing definitions now produces different P&L (verified by tests)

### 2. Warmup & Validity Gating

- New `valid_mask` parameter: boolean array marking bars where both indicators are non-NaN
- Signals on invalid bars are ignored
- No trades occur before both GMA and KAMA have warmed up
- Test verified: first trade occurs at index 54, after warmup completes at index 49

### 3. Start Policy

- **Default (`start_in_sync=False`)**: Start flat, first position change must be a buy edge
- **Optional (`start_in_sync=True`)**: Initialize position to regime at first valid bar, then trade on edges

### 4. Helper Functions

- `create_valid_mask(ind1, ind2)`: Returns boolean mask where both are non-NaN
- `compute_crossover_signals(ind1, ind2, cross_above)`: Computes strict crossover edges
  - `cross_above=True`: ind1 crosses ind2 from below (buy signal)
  - `cross_above=False`: ind1 crosses ind2 from above (sell signal)
- `diagnostic_first_trades()`: Returns indices of first few buy/sell events for debugging

### 5. Updated Return Signature

```python
port, final_val, trades, buy_count, sell_count = run_backtest_signals_nb(
    prices, buy_signal, sell_signal, initial_capital,
    start_in_sync=False, valid_mask=valid_mask
)
```

Now returns `buy_count` and `sell_count` separately for diagnostics.

### 6. Code Generator Updates (`backtest_builder.py`)

Generated scripts now:
- Import `create_valid_mask` and `compute_crossover_signals` helpers
- Compute validity mask once per (GMA, KAMA) pair
- Use `compute_crossover_signals()` instead of manual prev_ array logic
- Pass `valid_mask` to backtest engine
- Record `Buy_Count` and `Sell_Count` in results

### 7. Test Suite (`test_backtest_edge_driven.py`)

Five acceptance tests, all passing:

1. **Reversal Test**: Reversing crossover definition changes P&L
   - Example: GMA=20, KAMA=25: -4.28% → 12.06% (16.34% difference)
   
2. **Hold-All Sanity**: Always-long matches buy-and-hold
   - Error: 0.0000%
   
3. **Determinism**: Same inputs yield identical outputs
   - Verified: byte-for-byte identical
   
4. **Warmup Gating**: No trades before indicators are valid
   - First valid bar: 49, first trade: 54 ✓
   
5. **Grid Indexing**: Period N stored at grid[N] computes correctly
   - Error: 0.0000%

## Performance

- Speed unchanged: still uses Numba JIT, precomputed grids, and thread parallelization
- Only change is in how signals are interpreted (edge vs regime)
- No DataFrame iteration introduced

## Usage

### Running Tests

```bash
python test_backtest_edge_driven.py
```

### Generating Optimized Scripts

1. Open QuantForge app
2. Select GMA + KAMA indicators
3. Set crossover conditions (e.g., "GMA crosses KAMA from above")
4. Export code
5. Generated script will use edge-driven engine automatically

### Installing Dependencies

```bash
# Run installer (includes numba, numpy, joblib, tqdm)
install_dependencies.bat

# Or install manually
pip install -r requirements.txt
```

## Crossover Convention

**"GMA crosses KAMA from above"** means:
- Previous bar: GMA > KAMA
- Current bar: GMA < KAMA
- This is a **sell edge** (cross_above=False)

**"GMA crosses KAMA from below"** means:
- Previous bar: GMA < KAMA
- Current bar: GMA > KAMA
- This is a **buy edge** (cross_above=True)

## Diagnostics

Buy/sell counts are now tracked separately in results:
- `Number_of_Trades`: Total trades (buys only, since we start flat)
- `Buy_Count`: Number of buy edges executed
- `Sell_Count`: Number of sell edges executed

For debugging, use:
```python
from backtest_core import diagnostic_first_trades

diag = diagnostic_first_trades(buy_signal, sell_signal, valid_mask)
print(diag)
# {'buy_indices': [54, 259], 'sell_indices': [259, 461], 
#  'first_valid_index': 49, 'total_buys': 2, 'total_sells': 2}
```

## Files Changed

- `backtest_core.py`: Edge-driven engine with warmup gating
- `indicators_core.py`: No changes (already correct)
- `backtest_builder.py`: Updated code generator to use edge-driven API
- `results_parser.py`: Multi-sheet Excel support
- `requirements.txt`: Added numpy, numba, joblib, tqdm
- `install_dependencies.bat`: Installs from requirements.txt
- `check_installation.bat`: Checks numpy/numba/joblib/tqdm
- `test_backtest_edge_driven.py`: New test harness (all tests pass)

## Migration Notes

Old generated scripts (using manual prev_ arrays and regime checks) will continue to work but may produce incorrect results for crossover strategies. Regenerate scripts using the updated builder to get edge-driven behavior.

## References

- Test output: All 5 tests passing
- Reversal test confirms different P&L when definitions are swapped
- Grid indexing verified correct (period N at grid[N])
- Warmup verified: no trades before indicators are valid

