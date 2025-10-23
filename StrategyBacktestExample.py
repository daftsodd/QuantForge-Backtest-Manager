import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, time
from tqdm import tqdm
from joblib import Parallel, delayed
from tqdm_joblib import tqdm_joblib

# -----------------------------
# Configuration
# -----------------------------
n_cores = os.cpu_count() or 1
n_jobs  = max(1, int(n_cores * 0.52))

# -----------------------------
# 1. Load & Clean Data
# -----------------------------
def load_and_clean_data():
    path = r"E:\adamp\Documents\Visual Studio Code\Strategy development code\BitcoinData.csv"
    df   = pd.read_csv(path, sep=";", engine="python", quoting=3)
    df   = df.applymap(lambda x: x.strip('"') if isinstance(x, str) else x)
    df['Date'] = pd.to_datetime(
        df['timeOpen'],
        format="%Y-%m-%dT%H:%M:%S.%fZ",
        errors='coerce'
    )
    for col in ['open','high','low','close','volume','marketCap']:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return (
        df.drop_duplicates()
          .dropna(subset=['Date'])
          .sort_values('Date')
          .reset_index(drop=True)
    )

# -----------------------------
# 2. Indicator Functions
# -----------------------------
def compute_gma(series: pd.Series, window: int) -> pd.Series:
    N = int(window)
    if N < 1:
        return series.copy()
    return np.exp(
        np.log(series)
          .rolling(window=N, min_periods=N)
          .mean()
    )

def compute_kama(series: pd.Series, window: int,
                 fast_period: int = 2,
                 slow_period: int = 30) -> pd.Series:
    N = int(window)
    if N < 1:
        return series.copy()

    change     = series.diff(N).abs()
    volatility = series.diff().abs().rolling(window=N, min_periods=N).sum()
    er         = (change / volatility.replace(0, np.nan)).fillna(0)
    fast_sc    = 2 / (fast_period + 1)
    slow_sc    = 2 / (slow_period + 1)
    sc         = (er * (fast_sc - slow_sc) + slow_sc) ** 2

    kama = series.copy().astype(float)
    kama.iloc[:N] = series.iloc[:N]
    for t in range(N, len(series)):
        kama.iloc[t] = kama.iloc[t-1] + sc.iloc[t] * (series.iloc[t] - kama.iloc[t-1])
    return kama

# -----------------------------
# 3. Combine Indicators
# -----------------------------
def compute_indicators(df, gma_period, kama_period):
    df2 = df.copy()
    df2['GMA']  = compute_gma(df2['close'], window=gma_period)
    df2['KAMA'] = compute_kama(df2['close'], window=kama_period)
    return df2

# -----------------------------
# 4. Trading Logic (Flipped)
# -----------------------------
def strategy_logic(df):
    """
    BUY when GMA crosses KAMA from above,
    SELL when GMA crosses KAMA from below.
    """
    d = df.copy()
    d['prev_GMA']  = d['GMA'].shift(1)
    d['prev_KAMA'] = d['KAMA'].shift(1)
    d['buy_signal']  = (
        (d['prev_GMA']  > d['prev_KAMA']) &
        (d['GMA']       < d['KAMA'])
    )
    d['sell_signal'] = (
        (d['prev_GMA']  < d['prev_KAMA']) &
        (d['GMA']       > d['KAMA'])
    )
    return d

# -----------------------------
# 5. Backtest Engine
# -----------------------------
def run_backtest(df, initial_capital=10000):
    pos, cash, shares = 0, initial_capital, 0
    portfolio, trades = [], 0

    for _, r in df.iterrows():
        price = r['close']
        if pos == 0 and r.get('buy_signal', False):
            shares, cash, pos, trades = cash/price, 0, 1, trades+1
        elif pos == 1 and r.get('sell_signal', False):
            cash, shares, pos = shares*price, 0, 0
        portfolio.append(shares*price if pos else cash)

    port        = pd.Series(portfolio, index=df.index)
    final_val   = port.iloc[-1]
    ret         = port.pct_change().fillna(0)
    total_prof  = (final_val/initial_capital - 1) * 100
    sharpe      = (ret.mean()/ret.std()*np.sqrt(365)) if ret.std()!=0 else 0
    drawdown    = abs(((port - port.cummax())/port.cummax()).min() * 100)
    neg_ret     = ret[ret<0]
    sortino     = (ret.mean()*365)/(neg_ret.std()*np.sqrt(365)) \
                  if len(neg_ret)>0 and neg_ret.std()!=0 else 0
    omega       = ret[ret>0].sum() / abs(ret[ret<0].sum()) \
                  if ret[ret<0].sum()!=0 else float('inf')

    return {
        'Final_Portfolio_Value': final_val,
        'Total_Profit_%':       total_prof,
        'Max_Drawdown_%':       drawdown,
        'Number_of_Trades':     trades,
        'Sharpe_Ratio':         sharpe,
        'Sortino_Ratio':        sortino,
        'Omega_Ratio':          omega
    }

# -----------------------------
# 6. Parameter Sweep with Pause
# -----------------------------
def parameter_sweep(df, gma_range, kama_range,
                    initial_capital=10000, chunk_size=500):
    combos = [(g, k) for g in gma_range for k in kama_range]
    results, start = [], time.time()

    for i in range(0, len(combos), chunk_size):
        chunk = combos[i:i+chunk_size]
        def task(g, k):
            ind   = compute_indicators(df, g, k)
            strat = strategy_logic(ind)
            stats = run_backtest(strat, initial_capital)
            stats.update({'GMA_Period': g, 'KAMA_Period': k})
            return stats

        with tqdm_joblib(tqdm(total=len(chunk), desc="Chunk")):
            out = Parallel(n_jobs=n_jobs)(
                delayed(task)(g, k) for g, k in chunk
            )
        results.extend(out)

        if time.time() - start >= 5*60:
            print("Pausing for 5 minutes…")
            time.sleep(5*60)
            start = time.time()

    return pd.DataFrame(results)

# -----------------------------
# 7. Main Execution
# -----------------------------
if __name__ == "__main__":
    df_data    = load_and_clean_data()
    gma_range  = range(1, 101)
    kama_range = range(1, 101)

    results_df = parameter_sweep(df_data, gma_range, kama_range,
                                 initial_capital=10000,
                                 chunk_size=500)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_df.to_excel(
        os.path.join(script_dir, "Full_test_GMA_below_KAMA.xlsx"),
        index=False
    )

    # Heatmap of Total Profit
    pivot = results_df.pivot(
        index='GMA_Period',
        columns='KAMA_Period',
        values='Total_Profit_%'
    )
    plt.figure(figsize=(8,6))
    plt.imshow(pivot, cmap='viridis', origin='lower', aspect='auto')
    plt.colorbar(label='Total Profit (%)')
    plt.title('Heatmap: Buy GMA↘KAMA / Sell GMA↗KAMA')
    plt.xlabel('KAMA_Period'); plt.ylabel('GMA_Period')
    plt.tight_layout()
    plt.savefig(os.path.join(script_dir, "Heatmap_GMA_vs_KAMA_Flipped.png"))
    plt.close()
