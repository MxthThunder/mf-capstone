import os
import pandas as pd
from sqlalchemy import create_engine, text

# Base directories
workspace = r"c:\Datatatatta"
raw_dir = os.path.join(workspace, "data", "raw")
processed_dir = os.path.join(workspace, "data", "processed")
db_dir = os.path.join(workspace, "data", "db")
db_path = os.path.join(db_dir, "bluestock_mf.db")
sql_schema_path = os.path.join(workspace, "sql", "schema.sql")

# Ensure folders exist
os.makedirs(processed_dir, exist_ok=True)
os.makedirs(db_dir, exist_ok=True)

# Delete existing DB file for a clean start
if os.path.exists(db_path):
    try:
        os.remove(db_path)
    except Exception as e:
        print(f"Note: Could not delete old DB: {e}")

engine = create_engine(f"sqlite:///{db_path}")

print("=== STARTING CAPSTONE ETL PIPELINE ===")

# --- 1. CLEANING FUNCTIONS ---

def clean_fund_master(df):
    df['launch_date'] = pd.to_datetime(df['launch_date']).dt.strftime('%Y-%m-%d')
    return df

def clean_nav_history(df):
    df['date'] = pd.to_datetime(df['date'])
    df = df.drop_duplicates(subset=['amfi_code', 'date'])
    df = df[df['nav'] > 0]
    
    # Forward-fill weekend/holiday NAV gaps per scheme
    cleaned_groups = []
    for amfi_code, group in df.groupby('amfi_code'):
        group = group.sort_values('date')
        min_date = group['date'].min()
        max_date = group['date'].max()
        
        full_range = pd.date_range(start=min_date, end=max_date, freq='D')
        group = group.set_index('date').reindex(full_range)
        group['amfi_code'] = amfi_code
        group['nav'] = group['nav'].ffill()
        group = group.reset_index().rename(columns={'index': 'date'})
        cleaned_groups.append(group)
        
    df_cleaned = pd.concat(cleaned_groups, ignore_index=True)
    df_cleaned['date'] = df_cleaned['date'].dt.strftime('%Y-%m-%d')
    return df_cleaned

def clean_transactions(df):
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['transaction_type'] = df['transaction_type'].astype(str).str.strip()
    mapping = {
        'sip': 'SIP', 'Sip': 'SIP', 'SIP': 'SIP',
        'lumpsum': 'Lumpsum', 'Lumpsum': 'Lumpsum',
        'redemption': 'Redemption', 'Redemption': 'Redemption'
    }
    df['transaction_type'] = df['transaction_type'].map(lambda x: mapping.get(x, x))
    df = df[df['amount_inr'] > 0]
    df['kyc_status'] = df['kyc_status'].astype(str).str.strip().str.title()
    df['transaction_date'] = df['transaction_date'].dt.strftime('%Y-%m-%d')
    return df

def clean_performance(df):
    return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 'benchmark_3yr_pct']
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

# --- 2. LOAD DATA ---
print("Reading raw CSV files...")
df_fund = clean_fund_master(pd.read_csv(os.path.join(raw_dir, "01_fund_master.csv")))
df_nav = clean_nav_history(pd.read_csv(os.path.join(raw_dir, "02_nav_history.csv")))
df_aum = pd.read_csv(os.path.join(raw_dir, "03_aum_by_fund_house.csv"))
df_sip = pd.read_csv(os.path.join(raw_dir, "04_monthly_sip_inflows.csv"))
df_cat_inflows = pd.read_csv(os.path.join(raw_dir, "05_category_inflows.csv"))
df_industry_folio = pd.read_csv(os.path.join(raw_dir, "06_industry_folio_count.csv"))
df_perf = clean_performance(pd.read_csv(os.path.join(raw_dir, "07_scheme_performance.csv")))
df_tx = clean_transactions(pd.read_csv(os.path.join(raw_dir, "08_investor_transactions.csv")))
df_holdings = pd.read_csv(os.path.join(raw_dir, "09_portfolio_holdings.csv"))
df_bench = pd.read_csv(os.path.join(raw_dir, "10_benchmark_indices.csv"))

# Parse dates for other log tables
df_aum['date'] = pd.to_datetime(df_aum['date']).dt.strftime('%Y-%m-%d')
df_holdings['portfolio_date'] = pd.to_datetime(df_holdings['portfolio_date']).dt.strftime('%Y-%m-%d')
df_bench['date'] = pd.to_datetime(df_bench['date']).dt.strftime('%Y-%m-%d')

# --- 3. EXPORT CLEANED CSVS TO PROCESSED DIR ---
print("Exporting cleaned CSV files to data/processed/...")
df_fund.to_csv(os.path.join(processed_dir, "cleaned_fund_master.csv"), index=False)
df_nav.to_csv(os.path.join(processed_dir, "cleaned_nav_history.csv"), index=False)
df_aum.to_csv(os.path.join(processed_dir, "cleaned_aum_by_fund_house.csv"), index=False)
df_sip.to_csv(os.path.join(processed_dir, "cleaned_monthly_sip_inflows.csv"), index=False)
df_cat_inflows.to_csv(os.path.join(processed_dir, "cleaned_category_inflows.csv"), index=False)
df_industry_folio.to_csv(os.path.join(processed_dir, "cleaned_industry_folio_count.csv"), index=False)
df_perf.to_csv(os.path.join(processed_dir, "cleaned_scheme_performance.csv"), index=False)
df_tx.to_csv(os.path.join(processed_dir, "cleaned_investor_transactions.csv"), index=False)
df_holdings.to_csv(os.path.join(processed_dir, "cleaned_portfolio_holdings.csv"), index=False)
df_bench.to_csv(os.path.join(processed_dir, "cleaned_benchmark_indices.csv"), index=False)

# --- 4. DYNAMIC DATE DIMENSION ---
print("Building dynamic date dimension...")
all_dates = pd.concat([
    df_nav['date'],
    df_tx['transaction_date'],
    df_aum['date'],
    df_bench['date'],
    df_holdings['portfolio_date']
]).unique()

df_date = pd.DataFrame({'date': all_dates})
df_date['date_parsed'] = pd.to_datetime(df_date['date'])
df_date['year'] = df_date['date_parsed'].dt.year
df_date['quarter'] = df_date['date_parsed'].dt.quarter
df_date['month'] = df_date['date_parsed'].dt.month
df_date['day'] = df_date['date_parsed'].dt.day
df_date['is_weekend'] = df_date['date_parsed'].dt.dayofweek.isin([5, 6]).astype(int)
df_date['month_name'] = df_date['date_parsed'].dt.strftime('%B')
df_date = df_date.drop(columns=['date_parsed']).sort_values('date').reset_index(drop=True)
df_date.to_csv(os.path.join(processed_dir, "cleaned_date_dimension.csv"), index=False)

# --- 5. EXECUTE SCHEMA DDL ---
print("Initializing database schema from sql/schema.sql...")
with open(sql_schema_path, "r", encoding="utf-8") as f:
    schema_sql = f.read()

statements = [s.strip() for s in schema_sql.split(";") if s.strip()]
with engine.begin() as conn:
    for stmt in statements:
        conn.execute(text(stmt))

# --- 6. LOAD INTO SQLITE ---
print("Loading data into SQLite...")
df_fund.to_sql("dim_fund", engine, if_exists="append", index=False)
df_date.to_sql("dim_date", engine, if_exists="append", index=False)
df_nav.to_sql("fact_nav", engine, if_exists="append", index=False)
df_tx.to_sql("fact_transactions", engine, if_exists="append", index=False)

perf_cols = [
    'amfi_code', 'return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 
    'benchmark_3yr_pct', 'alpha', 'beta', 'sharpe_ratio', 'sortino_ratio', 
    'std_dev_ann_pct', 'max_drawdown_pct', 'aum_crore', 'morningstar_rating', 'risk_grade'
]
df_perf[perf_cols].to_sql("fact_performance", engine, if_exists="append", index=False)
df_aum.to_sql("fact_aum", engine, if_exists="append", index=False)
df_sip.to_sql("fact_monthly_sip_inflows", engine, if_exists="append", index=False)
df_cat_inflows.to_sql("fact_category_inflows", engine, if_exists="append", index=False)
df_industry_folio.to_sql("fact_industry_folio_count", engine, if_exists="append", index=False)
df_bench.to_sql("fact_benchmark_indices", engine, if_exists="append", index=False)
df_holdings.to_sql("fact_portfolio_holdings", engine, if_exists="append", index=False)

# --- 7. VERIFICATION AUDIT ---
print("\n--- LOAD AUDIT / VERIFICATION ---")
tables = [
    ("dim_fund", len(df_fund)),
    ("dim_date", len(df_date)),
    ("fact_nav", len(df_nav)),
    ("fact_transactions", len(df_tx)),
    ("fact_performance", len(df_perf)),
    ("fact_aum", len(df_aum)),
    ("fact_monthly_sip_inflows", len(df_sip)),
    ("fact_category_inflows", len(df_cat_inflows)),
    ("fact_industry_folio_count", len(df_industry_folio)),
    ("fact_benchmark_indices", len(df_bench)),
    ("fact_portfolio_holdings", len(df_holdings))
]

success = True
for name, expected in tables:
    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {name}")).scalar()
        if count == expected:
            print(f"[OK] Table '{name}': Count matches ({count} rows).")
        else:
            print(f"[FAIL] Table '{name}': Count MISMATCH! Expected {expected}, got {count}.")
            success = False

if success:
    print("\nETL Pipeline loaded bluestock_mf.db successfully!")
else:
    print("\nETL Pipeline loaded with count mismatches.")
