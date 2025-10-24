# QuantForge Backtest Builder - Quick Start Guide

## 🚀 Installation (First Time Only)

1. Run the installer:
   ```bash
   install_dependencies.bat
   ```

2. Verify installation:
   ```bash
   check_installation.bat
   ```

You should see all packages marked with checkmarks (✓).

## 📊 Generate Your First Optimized Strategy

### Step 1: Open the App
```bash
run_app.bat
```

### Step 2: Open Backtest Builder
- Click the **"Backtest Builder"** button in the main window

### Step 3: Configure Your Strategy

#### Indicators
- ✅ Check **GMA (Geometric Moving Average)**
- ✅ Check **KAMA (Kaufman Adaptive Moving Average)**

#### Trading Logic
- **Buy Condition:** "GMA crosses KAMA from below"
- **Sell Condition:** "GMA crosses KAMA from above"
- **Initial Capital:** $10,000
- **Periods/Year:** 365 (for daily data)
- **Fee Rate:** 0.0 (no fees) or 0.001 (0.1% fees)
- **Enable Short Selling:** ☐ Unchecked (long-only)

#### Parameter Sweep
- **GMA Start:** 1
- **GMA End:** 100
- **GMA Step:** 1
- **KAMA Start:** 1
- **KAMA End:** 100
- **KAMA Step:** 1

#### Performance
- **CPU Usage:** 52% (adjust based on your system)
- **Chunk Size:** 500
- **Pause Interval:** 5 minutes

#### Output
- **Excel Filename:** backtest_results.xlsx
- **Generate Heatmap:** ✓ Checked
- **Heatmap Metric:** Total_Profit_%

### Step 4: Export Code
- Click **"Export Code..."**
- Script saved to `Generated_Strategies/` folder
- Add to File Browser if prompted

### Step 5: Run the Strategy
- Select the script in File Browser
- Click **"Execute"**
- Watch progress in console
- Results will be displayed automatically

### Step 6: Analyze Results

**Excel File Contains:**
- `All_Results` - All 10,000 parameter combinations
- `Top5_Sharpe` - Best 5 by Sharpe Ratio
- `Top5_Sortino` - Best 5 by Sortino Ratio
- `Top5_Omega` - Best 5 by Omega Ratio
- `Top5_MaxDD` - Best 5 by Max Drawdown
- `Top5_Profit` - Best 5 by Total Profit %

**Heatmap:** Visual representation of performance across parameter space

## 💡 Common Scenarios

### Scenario 1: Daily Data (Default)
```
Periods/Year: 365
Fee Rate: 0.0
Short Selling: OFF (long-only)
```

### Scenario 2: Trading Days Only
```
Periods/Year: 252  # Only trading days, not weekends
Fee Rate: 0.001    # 0.1% exchange fees
Short Selling: OFF
```

### Scenario 3: Hourly Data
```
Periods/Year: 8760  # 24 × 365
Fee Rate: 0.002     # Higher fees for more frequent trading
Short Selling: OFF
```

### Scenario 4: Long/Short Strategy
```
Periods/Year: 365
Fee Rate: 0.001
Short Selling: ON  # Always in market (long or short)
```

## 🔍 Understanding Results

### Key Metrics

- **Total_Profit_%**: Raw return (positive = profit, negative = loss)
- **Sharpe_Ratio**: Risk-adjusted return (higher = better, > 1 is good)
- **Sortino_Ratio**: Like Sharpe but only penalizes downside volatility
- **Omega_Ratio**: Probability-weighted gains/losses (> 1 is good)
- **Max_Drawdown_%**: Largest peak-to-trough decline (lower = better)
- **Number_of_Trades**: Total trades executed
- **Buy_Count / Sell_Count**: Separate buy and sell counts

### Interpreting Top-5 Tables

1. **Top5_Sharpe**: Best risk-adjusted returns
   - Good for consistent performance with controlled risk
   - Look for Sharpe > 2.0 for excellent strategies

2. **Top5_Profit**: Highest raw returns
   - May have high volatility or drawdowns
   - Check Max_Drawdown_% to assess risk

3. **Top5_MaxDD**: Lowest drawdowns
   - Most conservative configurations
   - May have lower returns but safer

4. **Top5_Sortino**: Best downside-adjusted returns
   - Better than Sharpe if you don't care about upside volatility
   - Useful for asymmetric strategies

5. **Top5_Omega**: Best probability-weighted outcomes
   - Alternative risk measure
   - > 1.5 is generally good

### Reading the Heatmap

- **X-axis**: KAMA period
- **Y-axis**: GMA period
- **Color**: Performance metric (brighter = better for most metrics)
- **Patterns**: Look for clusters of high performance
- **Diagonal**: Often shows interesting patterns (GMA ≈ KAMA)

## ⚠️ Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'numba'"
**Solution:** Run `install_dependencies.bat`

### Issue 2: Excel file permission denied
**Solution:** Close any open Excel windows showing the results file, then try again

### Issue 3: App crashes when toggling heatmap
**Solution:** Already fixed! Heatmaps now have unique filenames

### Issue 4: Slow backtest
**Solution:** 
- Reduce parameter sweep range (e.g., 1-50 instead of 1-100)
- Increase chunk size (e.g., 1000 instead of 500)
- Increase CPU usage % (e.g., 75% instead of 52%)

## 🧪 Testing Your Installation

Run the test suites to verify everything works:

```bash
# Test edge-driven backtest (7 tests)
python test_backtest_edge_driven.py

# Test indicator order handling (3 tests)
python test_indicator_order.py

# Test exposure toggle (3 tests)
python test_exposure_toggle.py
```

All should show "ALL TESTS PASSED" ✓

## 📚 Learning More

### Documentation Files
- `COMPLETE_OPTIMIZATION.md` - This guide (comprehensive)
- `INTEGRATION_COMPLETE.md` - Integration details
- `INDICATOR_ORDER_FIX.md` - How indicator order is parsed
- `EDGE_DRIVEN_BACKTEST.md` - Edge-driven semantics
- `README.md` - General app documentation

### Understanding Crossovers

**"GMA crosses KAMA from below"** means:
- Previous bar: GMA < KAMA
- Current bar: GMA > KAMA
- **Action**: Enter long position (GMA rising above KAMA)

**"GMA crosses KAMA from above"** means:
- Previous bar: GMA > KAMA
- Current bar: GMA < KAMA
- **Action**: Exit position (GMA falling below KAMA)

**Important:** Reversing the indicator order changes the strategy!
- "GMA crosses KAMA" ≠ "KAMA crosses GMA"
- This is now correctly handled (was a bug before)

## 🎯 Next Steps

1. **Run a small test** (1-10 range) to verify your data loads correctly
2. **Expand the sweep** to full range (1-100) for comprehensive testing
3. **Analyze Top-5 results** to find optimal parameters
4. **Export best configurations** for live trading or further analysis
5. **Experiment with different indicators** (SMA coming soon)
6. **Try long/short mode** to see if it improves performance

## 💪 You're Ready!

The QuantForge Backtest Builder is now optimized and ready to use. Generate your strategies and start backtesting!

**Key Improvements:**
- 🚀 10-100× faster (Numba + precomputation)
- ✅ Correct results (indicator order, annualization)
- 📊 Multi-sheet Excel (Top-5 tables)
- 🎛️ Long/short support
- 🧪 13/13 tests passing

Happy backtesting! 🎉

