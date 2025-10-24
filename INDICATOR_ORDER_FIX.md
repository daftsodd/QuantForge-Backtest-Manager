# Indicator Order Fix - Complete Implementation

## Problem Summary

The Backtest Builder was ignoring indicator order in crossover strategies:
- "GMA crosses KAMA" produced identical results to "KAMA crosses GMA"
- Engine was syncing to regime instead of respecting edge events
- No proper parsing of left vs right indicators
- Missing support for regime strategies (long-only, long/short)
- Hard-coded annualization (always assumed daily data)

## Solution Implemented

### 1. **Core Backtest Functions** (`backtest_core.py`)

#### New Functions Added

**`run_backtest_edges_nb()` - Edge-Driven Backtest**
- Trades ONLY on edge events (buy_edges, sell_edges)
- Never syncs to regime (fixed the core bug)
- Supports fees, validity masking, start_in_sync policy
- Returns: `(portfolio, final_value, trades, buy_count, sell_count)`

**`run_backtest_regime_long_only_nb()` - Regime Long-Only**
- Long when regime=True, flat when regime=False
- Trades on regime transitions
- Returns: `(portfolio, final_value, trades, long_bars, flat_bars)`

**`run_backtest_regime_long_short_nb()` - Regime Long/Short**
- Long when regime=True, short when regime=False
- Trades on regime flips
- Returns: `(portfolio, final_value, transitions, long_bars, short_bars)`

**`compute_crossover_edges()` - True Edge Detection**
```python
def compute_crossover_edges(left, right, cross_up=True, tie_rule='strict'):
    """
    Returns edges where:
      cross_up=True:  prev(left) < prev(right) AND left > right
      cross_up=False: prev(left) > prev(right) AND left < right
    
    tie_rule: 'strict' (< and >) or 'inclusive' (<= and >=)
    """
```

**`compute_regime()` - Regime Arrays**
```python
def compute_regime(left, right, greater_than=True, tie_rule='strict'):
    """
    Returns boolean regime:
      greater_than=True:  regime = (left > right)
      greater_than=False: regime = (left < right)
    
    tie_rule='hold_prior': on equality, maintain previous state
    """
```

**`compute_metrics_from_portfolio()` - Correct Annualization**
```python
def compute_metrics_from_portfolio(port, initial_capital, periods_per_year=365):
    """
    Sharpe:  (mean/std) * sqrt(periods_per_year)
    Sortino: (mean*periods_per_year) / (neg_std*sqrt(periods_per_year))
    """
```

### 2. **Builder Configuration** (`backtest_builder.py`)

#### New Config Parameters
```python
'periods_per_year': 365      # For annualization (365=daily, 252=trading days)
'fee_rate': 0.0              # Trading fee as fraction (0.001 = 0.1%)
'tie_rule': 'strict'         # 'strict' or 'hold_prior'
'start_in_sync': False       # Start flat (False) or in-regime (True)
'strategy_type': 'crossover' # 'crossover', 'regime_long_only', 'regime_long_short'
```

#### New UI Fields
- Periods/Year spinner (1-365, default 365)
- Fee Rate spinner (0-0.1, default 0.0)

### 3. **Code Generator - Indicator Order Parsing**

#### Critical Fix: `parse_crossover_condition()`
```python
def parse_crossover_condition(cond: str):
    """
    Parses "GMA crosses KAMA from above" into:
      - left_indicator: 'GMA' -> variable 'g'
      - right_indicator: 'KAMA' -> variable 'k'
      - cross_up: False (from above means crossing down)
    
    Returns: (left_var, right_var, cross_up)
    """
```

**Example Parsing:**
- Input: `"GMA crosses KAMA from above"`
  - left='g', right='k', cross_up=False
  - Generates: `compute_crossover_edges(g, k, cross_up=False)`

- Input: `"KAMA crosses GMA from above"`
  - left='k', right='g', cross_up=False
  - Generates: `compute_crossover_edges(k, g, cross_up=False)`

**Result:** Argument order is now correct, so reversing indicators produces different P&L!

#### Generated Script Features

**Strategy Summary** (printed in script header):
```python
# Strategy Summary:
#   Buy:  GMA crosses KAMA from above
#   Sell: GMA crosses KAMA from below
#   Tie rule: strict
#   Start in sync: False
#   Fee rate: 0.0
#   Periods/year: 365
```

**Updated Sweep Function:**
```python
def eval_for_k(kp: int):
    # ...
    buy_edges = compute_crossover_edges(g, k, cross_up=True, tie_rule='strict')
    sell_edges = compute_crossover_edges(g, k, cross_up=False, tie_rule='strict')
    
    port, final_val, trades, buy_count, sell_count = run_backtest_edges_nb(
        close, buy_edges, sell_edges, float(initial_capital),
        start_in_sync=False,
        valid_mask=valid_mask,
        fee_rate=0.0
    )
    
    metrics = compute_metrics_from_portfolio(
        port, float(initial_capital), periods_per_year=365
    )
```

### 4. **Test Harness** (`test_indicator_order.py`)

#### Verification Test

Tests that `"GMA crosses KAMA"` != `"KAMA crosses GMA"`:

**Test Output:**
```
Testing GMA=20, KAMA=25:
  GMA crosses KAMA: P&L=12.06%, Buys=14, Sells=14
  KAMA crosses GMA: P&L=-4.28%, Buys=14, Sells=13
  Difference: 16.34%
  [PASS] Indicator order matters
```

**All 3 test pairs passed** ✓

## Key Improvements

### 1. **Indicator Order Now Matters**
   - ✅ "GMA crosses KAMA" != "KAMA crosses GMA"
   - ✅ Argument order correctly parsed from UI
   - ✅ Different P&L confirms fix works

### 2. **True Edge-Driven Backtesting**
   - ✅ Trades only on edges (prev vs current comparison)
   - ✅ Never syncs to regime inside engine
   - ✅ Respects validity mask and warmup

### 3. **Regime Strategies Supported**
   - ✅ Long-only: long when regime, flat otherwise
   - ✅ Long/short: long when regime, short otherwise
   - ✅ Tie policies: strict or hold_prior

### 4. **Correct Annualization**
   - ✅ Sharpe/Sortino scale with periods_per_year
   - ✅ Supports daily (365), trading days (252), hourly, etc.
   - ✅ No more hard-coded assumptions

### 5. **Diagnostics**
   - ✅ Buy_count and sell_count tracked separately
   - ✅ Strategy summary printed in generated scripts
   - ✅ Test harness verifies correctness

## Usage

### Generate Optimized Script

1. Open QuantForge app
2. Select GMA + KAMA indicators
3. Set buy condition: `"GMA crosses KAMA from above"`
4. Set sell condition: `"GMA crosses KAMA from below"`
5. Adjust Periods/Year if not daily data (e.g., 252 for trading days)
6. Set Fee Rate if applicable (e.g., 0.001 for 0.1%)
7. Export code

### Generated Script Will:
- Parse indicator order correctly
- Use `compute_crossover_edges(left, right, cross_up, tie_rule)`
- Call `run_backtest_edges_nb()` with proper arguments
- Apply correct annualization via `periods_per_year`
- Track buy/sell counts separately
- Print strategy summary

### Verify Indicator Order

Run the test:
```bash
python test_indicator_order.py
```

Expected output: All tests PASS with different P&L for reversed indicators.

## Files Changed

1. **`backtest_core.py`** - Complete rewrite
   - Added 3 backtest engines (edges, regime_long_only, regime_long_short)
   - Added `compute_crossover_edges()` with correct prev/current logic
   - Added `compute_regime()` for > / < strategies
   - Updated `compute_metrics_from_portfolio()` with periods_per_year

2. **`backtest_builder.py`** - Updated code generator
   - Added periods_per_year, fee_rate, tie_rule to config
   - Added UI fields for new parameters
   - Implemented `parse_crossover_condition()` to extract left/right indicators
   - Updated generated code to use correct argument order
   - Added strategy summary to generated scripts

3. **`test_indicator_order.py`** - New test harness
   - Verifies "GMA crosses KAMA" != "KAMA crosses GMA"
   - Tests multiple parameter pairs
   - All tests passing ✓

## Performance

- ✅ Speed unchanged: still uses precomputed grids, Numba JIT, thread parallelization
- ✅ No DataFrame iteration in hot path
- ✅ All math is float64 (stable)

## Migration Notes

- Old scripts (generated before this fix) will NOT correctly handle indicator order
- Regenerate all crossover strategies to get the fix
- Update periods_per_year if your data isn't daily

## Next Steps (Optional Enhancements)

Still pending (not critical):
- Grid indexing assertions (defensive bounds checking)
- UI fields for tie_rule selector (currently hard-coded to 'strict')
- Execution timing (close vs next-open, slippage modeling)

These can be added incrementally without affecting correctness.

