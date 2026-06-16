"""
Bluestock Mutual Fund Performance Metrics Calculator.
This script connects to the SQLite star schema database, queries daily NAV histories,
and computes annualized CAGR, Sharpe Ratio (relative to 6% risk-free rate), Beta vs Benchmark Index,
and 95% Daily Value at Risk (VaR) for all registered schemes.
"""
import os
import sqlite3
import pandas as pd
import numpy as np

# Paths
workspace = r"c:\Datatatatta"
db_path = os.path.join(workspace, "data", "db", "bluestock_mf.db")
processed_dir = os.path.join(workspace, "data", "processed")

if not os.path.exists(db_path):
    print("Error: Database not found!")
    exit(1)

conn = sqlite3.connect(db_path)

# 1. Fetch schemes and their benchmarks
funds = pd.read_sql_query("SELECT amfi_code, scheme_name, benchmark FROM dim_fund", conn)

# 2. Daily risk-free rate (6% annual, divided by 252 trading days)
rf_annual = 0.06
rf_daily = rf_annual / 252

metrics_list = []

print("Computing performance metrics (Sharpe, Beta, CAGR, VaR) for all schemes...")

for idx, row in funds.iterrows():
    amfi_code = int(row['amfi_code'])
    scheme_name = row['scheme_name']
    benchmark_name = row['benchmark']
    
    # Get daily NAV history
    nav_df = pd.read_sql_query(f"""
        SELECT date, nav FROM fact_nav 
        WHERE amfi_code = {amfi_code}
        ORDER BY date
    """, conn)
    
    if len(nav_df) < 2:
        continue
        
    nav_df['date'] = pd.to_datetime(nav_df['date'])
    nav_df['returns'] = nav_df['nav'].pct_change()
    
    # Calculate CAGR using trading days (252 per year)
    nav_begin = nav_df['nav'].iloc[0]
    nav_end = nav_df['nav'].iloc[-1]
    n_trading_days = len(nav_df) - 1
    
    if n_trading_days > 0 and nav_begin > 0 and nav_end > 0:
        cagr = (nav_end / nav_begin) ** (252.0 / n_trading_days) - 1
    else:
        cagr = 0.0
        
    # Calculate Sharpe Ratio (Annualized)
    returns_clean = nav_df['returns'].dropna()
    mean_return = returns_clean.mean()
    std_return = returns_clean.std()
    
    if std_return > 0:
        sharpe = ((mean_return - rf_daily) / std_return) * np.sqrt(252)
    else:
        sharpe = 0.0
        
    # Calculate Value at Risk (VaR) at 95% confidence (5th percentile of daily returns)
    if len(returns_clean) > 0:
        var_95 = np.percentile(returns_clean, 5)
    else:
        var_95 = 0.0
        
    # Calculate Beta vs Benchmark
    # Fetch daily close value of matching benchmark index
    bench_df = pd.read_sql_query(f"""
        SELECT date, close_value FROM fact_benchmark_indices
        WHERE index_name = ?
        ORDER BY date
    """, conn, params=(benchmark_name,))
    
    beta = 0.0
    if not bench_df.empty:
        bench_df['date'] = pd.to_datetime(bench_df['date'])
        bench_df['bench_returns'] = bench_df['close_value'].pct_change()
        
        # Merge on date to align returns
        merged = pd.merge(nav_df[['date', 'returns']], bench_df[['date', 'bench_returns']], on='date').dropna()
        if len(merged) > 10:
            cov = np.cov(merged['returns'], merged['bench_returns'])[0, 1]
            var_bench = np.var(merged['bench_returns'], ddof=1)
            if var_bench > 0:
                beta = cov / var_bench
                
    metrics_list.append({
        'amfi_code': amfi_code,
        'scheme_name': scheme_name,
        'cagr_pct': round(cagr * 100, 4),
        'sharpe_ratio': round(sharpe, 4),
        'beta': round(beta, 4),
        'var_95_daily_pct': round(var_95 * 100, 4)
    })

df_metrics = pd.DataFrame(metrics_list)
output_path = os.path.join(processed_dir, "computed_performance_metrics.csv")
df_metrics.to_csv(output_path, index=False)
print(f"Computed performance metrics for {len(df_metrics)} schemes and saved to {output_path}")

conn.close()
