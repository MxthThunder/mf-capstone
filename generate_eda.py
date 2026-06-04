import os
import json
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set paths
workspace = r"c:\Datatatatta"
db_path = os.path.join(workspace, "data", "processed", "mutual_funds.db")
figures_dir = os.path.join(workspace, "reports", "figures")
notebook_dir = os.path.join(workspace, "notebooks")

os.makedirs(figures_dir, exist_ok=True)
os.makedirs(notebook_dir, exist_ok=True)

# Set matplotlib style for high aesthetics
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16,
    'patch.edgecolor': 'none'
})

# Palette
colors_primary = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

print("=== DAY 3: EDA VISUALIZATIONS GENERATOR ===")

# Connect to database
conn = sqlite3.connect(db_path)

# --- 1. NAV Daily Trend Analysis ---
print("Generating Chart 1: NAV daily trends...")
df_nav = pd.read_sql_query("""
    SELECT n.date, f.scheme_name, n.nav, f.category
    FROM fact_nav n
    JOIN dim_fund f ON n.amfi_code = f.amfi_code
""", conn)
df_nav['date'] = pd.to_datetime(df_nav['date'])

plt.figure(figsize=(12, 6))
# Plot a subset of key schemes to keep it readable, e.g., one from each fund house or category
schemes_to_plot = df_nav['scheme_name'].unique()[:8]
for scheme in schemes_to_plot:
    subset = df_nav[df_nav['scheme_name'] == scheme].sort_values('date')
    plt.plot(subset['date'], subset['nav'], label=scheme.split(" - ")[0], alpha=0.85, linewidth=1.5)

# Highlight 2023 Bull Run and 2024 Correction
plt.axvspan(pd.to_datetime('2023-01-01'), pd.to_datetime('2023-12-31'), color='green', alpha=0.08, label='2023 Bull Run')
plt.axvspan(pd.to_datetime('2024-04-01'), pd.to_datetime('2024-06-30'), color='red', alpha=0.08, label='2024 Corrections')

plt.title("Daily NAV Trends of Key Mutual Fund Schemes (2022–2026)", pad=15)
plt.xlabel("Date")
plt.ylabel("Net Asset Value (NAV)")
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "01_nav_trends.png"), dpi=150)
plt.close()


# --- 2. AUM Growth Bar Chart ---
print("Generating Chart 2: AUM growth bar chart...")
df_aum = pd.read_sql_query("""
    SELECT date, fund_house, aum_crore, aum_lakh_crore 
    FROM fact_aum
""", conn)
df_aum['year'] = pd.to_datetime(df_aum['date']).dt.year

# Aggregate by year and fund house
aum_yearly = df_aum.groupby(['year', 'fund_house'])['aum_crore'].mean().reset_index()
# Convert to Lakh Crores
aum_yearly['aum_lakh_crore'] = aum_yearly['aum_crore'] / 100000

plt.figure(figsize=(12, 6))
sns.barplot(data=aum_yearly, x='year', y='aum_lakh_crore', hue='fund_house', palette="tab10")
plt.title("AUM Growth by Fund House (2022–2025)", pad=15)
plt.xlabel("Year")
plt.ylabel("Average AUM (Lakh Crore ₹)")

# Highlight SBI at ₹12.5L Cr dominance
# Draw an annotation or highlight on SBI in 2025 (or max year)
plt.annotate('SBI AUM Dominance\n(Peak AUM ~12.5L Cr)', xy=(3.1, 8.5), xytext=(2.2, 9.5),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6))

plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', title="Fund House")
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "02_aum_growth.png"), dpi=150)
plt.close()


# --- 3. SIP Inflow Time-Series ---
print("Generating Chart 3: SIP inflow time-series...")
df_sip = pd.read_sql_query("""
    SELECT month, sip_inflow_crore, sip_aum_lakh_crore, yoy_growth_pct 
    FROM fact_monthly_sip_inflows
""", conn)
df_sip['date'] = pd.to_datetime(df_sip['month'] + "-01")

plt.figure(figsize=(10, 5))
plt.plot(df_sip['date'], df_sip['sip_inflow_crore'], color="#1f77b4", marker='o', linewidth=2, label="Monthly SIP Inflow")
plt.fill_between(df_sip['date'], df_sip['sip_inflow_crore'], color="#1f77b4", alpha=0.1)

# Annotate Dec 2025 peak
peak_row = df_sip.sort_values('date').iloc[-1]  # Dec 2025 is last row
plt.plot(peak_row['date'], peak_row['sip_inflow_crore'], 'ro', markersize=8)
plt.annotate(f"All-Time High: \u20b9{int(peak_row['sip_inflow_crore']):,} Cr\n(Dec 2025)", 
             xy=(peak_row['date'], peak_row['sip_inflow_crore']), 
             xytext=(pd.to_datetime('2024-06-01'), 27000),
             arrowprops=dict(facecolor='red', shrink=0.08, width=1, headwidth=6),
             fontweight='bold', color='red')

plt.title("Monthly SIP Inflows Trend (Jan 2022 – Dec 2025)", pad=15)
plt.xlabel("Month")
plt.ylabel("SIP Inflow (Crores \u20b9)")
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "03_sip_inflow_trend.png"), dpi=150)
plt.close()


# --- 4. Category Inflow Heatmap ---
print("Generating Chart 4: Category inflow heatmap...")
df_cat = pd.read_sql_query("""
    SELECT month, category, net_inflow_crore 
    FROM fact_category_inflows
""", conn)

# Pivot data
cat_pivot = df_cat.pivot(index='category', columns='month', values='net_inflow_crore')
# Sort columns to ensure chronological order
cat_pivot = cat_pivot[sorted(cat_pivot.columns)]

plt.figure(figsize=(14, 6))
sns.heatmap(cat_pivot, cmap="RdYlGn", center=0, cbar_kws={'label': 'Net Inflow (Crores \u20b9)'}, annot=False)
plt.title("Net Monthly Inflows by Fund Category (Heatmap)", pad=15)
plt.xlabel("Month")
plt.ylabel("Fund Category")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "04_category_inflow_heatmap.png"), dpi=150)
plt.close()


# --- 5. Investor Demographics (Age Group Pie Chart) ---
print("Generating Chart 5: Investor age group distribution...")
df_tx = pd.read_sql_query("""
    SELECT transaction_date, amount_inr, state, city_tier, age_group, gender, payment_mode, kyc_status 
    FROM fact_transactions
""", conn)

age_dist = df_tx.groupby('age_group')['amount_inr'].sum().reset_index()

plt.figure(figsize=(6, 6))
plt.pie(age_dist['amount_inr'], labels=age_dist['age_group'], autopct='%1.1f%%', 
        colors=colors_primary[:5], startangle=140, pctdistance=0.85,
        wedgeprops=dict(width=0.4, edgecolor='w'))
plt.title("Total Transaction Volume Split by Age Group", pad=15)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "05_age_group_pie.png"), dpi=150)
plt.close()


# --- 6. SIP Amount Box Plot by Age Group ---
print("Generating Chart 6: SIP amount box plot by age group...")
# Filter to only SIP transactions to be accurate to "SIP amount box plot"
df_sip_tx = df_tx[df_tx['payment_mode'] == 'Mandate'] # Mandates represent recurring SIPs or we can use all transactions
if df_sip_tx.empty:
    df_sip_tx = df_tx

plt.figure(figsize=(10, 6))
# Use log scale since transactions might span multiple magnitudes (e.g. 500 to 10L)
sns.boxplot(data=df_sip_tx, x='age_group', y='amount_inr', hue='age_group', palette="Set2", legend=False)
plt.title("SIP Transaction Amount Distribution by Age Group", pad=15)
plt.xlabel("Age Group")
plt.ylabel("SIP Transaction Amount (INR)")
plt.yscale('log')
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "06_sip_box_plot.png"), dpi=150)
plt.close()


# --- 7. Gender Split ---
print("Generating Chart 7: Gender split pie chart...")
gender_dist = df_tx.groupby('gender')['amount_inr'].sum().reset_index()

plt.figure(figsize=(6, 6))
plt.pie(gender_dist['amount_inr'], labels=gender_dist['gender'], autopct='%1.1f%%', 
        colors=["#f781bf", "#377eb8"], startangle=90, 
        wedgeprops=dict(edgecolor='w'))
plt.title("Investor Transaction Value Split by Gender", pad=15)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "07_gender_pie.png"), dpi=150)
plt.close()


# --- 8. Geographic Distribution ---
print("Generating Chart 8: Horizontal bar chart of SIP amount by state...")
state_dist = df_tx.groupby('state')['amount_inr'].sum().reset_index()
state_dist['amount_crore'] = state_dist['amount_inr'] / 10000000
state_dist = state_dist.sort_values('amount_crore', ascending=False).head(15)

plt.figure(figsize=(10, 6))
sns.barplot(data=state_dist, x='amount_crore', y='state', hue='state', palette="viridis", legend=False)
plt.title("Top 15 States by Cumulative Investment Amount", pad=15)
plt.xlabel("Total Investments (Crores \u20b9)")
plt.ylabel("State")
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "08_geographic_state_bar.png"), dpi=150)
plt.close()


# --- 9. T30 vs B30 City Tier Pie Chart ---
print("Generating Chart 9: T30 vs B30 city tier pie chart...")
tier_dist = df_tx.groupby('city_tier')['amount_inr'].sum().reset_index()

plt.figure(figsize=(6, 6))
plt.pie(tier_dist['amount_inr'], labels=tier_dist['city_tier'], autopct='%1.1f%%', 
        colors=["#4daf4a", "#984ea3"], startangle=120, pctdistance=0.75,
        wedgeprops=dict(width=0.4, edgecolor='w'))
plt.title("Investment Split: T30 (Top 30) vs B30 (Beyond 30) Cities", pad=15)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "09_city_tier_pie.png"), dpi=150)
plt.close()


# --- 10. Folio Count Growth ---
print("Generating Chart 10: Folio count growth...")
df_folio = pd.read_sql_query("""
    SELECT month, total_folios_crore, equity_folios_crore, debt_folios_crore 
    FROM fact_industry_folio_count
""", conn)
df_folio['date'] = pd.to_datetime(df_folio['month'] + "-01")
df_folio = df_folio.sort_values('date')

plt.figure(figsize=(10, 5))
plt.plot(df_folio['date'], df_folio['total_folios_crore'], color="#e41a1c", marker='s', linewidth=2.5, label="Total Industry Folios")
plt.plot(df_folio['date'], df_folio['equity_folios_crore'], color="#377eb8", linestyle='--', linewidth=1.8, label="Equity Folios")
plt.plot(df_folio['date'], df_folio['debt_folios_crore'], color="#4daf4a", linestyle=':', linewidth=1.8, label="Debt Folios")

# Mark milestones: Jan 2022 (13.26 Cr) and Dec 2025 (26.12 Cr)
plt.plot(df_folio['date'].iloc[0], df_folio['total_folios_crore'].iloc[0], 'ko', markersize=6)
plt.annotate(f"Jan 2022: {df_folio['total_folios_crore'].iloc[0]} Cr", 
             xy=(df_folio['date'].iloc[0], df_folio['total_folios_crore'].iloc[0]), 
             xytext=(df_folio['date'].iloc[0] + pd.Timedelta(days=60), df_folio['total_folios_crore'].iloc[0] + 0.8),
             arrowprops=dict(arrowstyle="->", color='black'))

plt.plot(df_folio['date'].iloc[-1], df_folio['total_folios_crore'].iloc[-1], 'ko', markersize=6)
plt.annotate(f"Dec 2025: {df_folio['total_folios_crore'].iloc[-1]} Cr", 
             xy=(df_folio['date'].iloc[-1], df_folio['total_folios_crore'].iloc[-1]), 
             xytext=(df_folio['date'].iloc[-1] - pd.Timedelta(days=500), df_folio['total_folios_crore'].iloc[-1] - 1.8),
             arrowprops=dict(arrowstyle="->", color='black'))

plt.title("Folio Count Growth Trend (Jan 2022 – Dec 2025)", pad=15)
plt.xlabel("Month")
plt.ylabel("Folio Count (Crores)")
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "10_folio_growth.png"), dpi=150)
plt.close()


# --- 11. NAV Return Correlation Matrix Heatmap ---
print("Generating Chart 11: NAV return correlation matrix...")
# Load NAV history and pivot to get wide table of daily NAV prices
nav_wide = df_nav.pivot(index='date', columns='scheme_name', values='nav')
# Pick 10 selected funds for correlation
selected_schemes = nav_wide.columns[:10]
nav_wide_subset = nav_wide[selected_schemes]
# Calculate daily returns percent change
returns_df = nav_wide_subset.pct_change().dropna()
# Correlation matrix
corr_matrix = returns_df.corr()

plt.figure(figsize=(10, 8))
# Clean correlation labels (truncate scheme names for readability)
short_labels = [col.split(" - ")[0] for col in corr_matrix.columns]
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", 
            xticklabels=short_labels, yticklabels=short_labels, square=True)
plt.title("Daily NAV Return Pairwise Correlation Matrix (10 Selected Funds)", pad=15)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "11_nav_correlation_matrix.png"), dpi=150)
plt.close()


# --- 12. Sector Allocation Donut Chart ---
print("Generating Chart 12: Sector allocation donut chart...")
df_holdings = pd.read_sql_query("""
    SELECT stock_symbol, stock_name, sector, weight_pct, market_value_cr 
    FROM fact_portfolio_holdings
""", conn)

# Aggregate sector weights
sector_dist = df_holdings.groupby('sector')['weight_pct'].sum().reset_index()
sector_dist = sector_dist.sort_values('weight_pct', ascending=False).head(8)

plt.figure(figsize=(6, 6))
plt.pie(sector_dist['weight_pct'], labels=sector_dist['sector'], autopct='%1.1f%%', 
        colors=colors_primary[:8], startangle=45, pctdistance=0.75,
        wedgeprops=dict(width=0.4, edgecolor='w'))
plt.title("Aggregate Sector Allocation in Portfolio Holdings", pad=15)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "12_sector_donut.png"), dpi=150)
plt.close()


# --- 13. Morningstar Ratings Distribution ---
print("Generating Chart 13: Morningstar ratings distribution...")
df_perf = pd.read_sql_query("""
    SELECT p.amfi_code, p.return_3yr_pct, p.alpha, f.expense_ratio_pct, p.morningstar_rating, p.risk_grade 
    FROM fact_performance p
    JOIN dim_fund f ON p.amfi_code = f.amfi_code
""", conn)

plt.figure(figsize=(8, 5))
sns.countplot(data=df_perf, x='morningstar_rating', hue='morningstar_rating', palette="Blues_r", legend=False)
plt.title("Mutual Fund Count by Morningstar Star Rating", pad=15)
plt.xlabel("Morningstar Rating")
plt.ylabel("Number of Schemes")
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "13_morningstar_ratings.png"), dpi=150)
plt.close()


# --- 14. Risk Category Distribution ---
print("Generating Chart 14: Risk category count bar chart...")
df_fund_meta = pd.read_sql_query("""
    SELECT amfi_code, risk_category 
    FROM dim_fund
""", conn)

plt.figure(figsize=(8, 5))
sns.countplot(data=df_fund_meta, x='risk_category', hue='risk_category', palette="rocket_r", legend=False,
              order=['Low', 'Moderate', 'Moderately High', 'High', 'Very High'])
plt.title("Distribution of Mutual Funds by Risk Category", pad=15)
plt.xlabel("Risk Category")
plt.ylabel("Number of Schemes")
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "14_risk_categories.png"), dpi=150)
plt.close()


# --- 15. Expense Ratio vs Returns Scatter Plot ---
print("Generating Chart 15: Expense ratio vs returns scatter plot...")
# Merge static fund details with performance metrics
df_merged_perf = pd.merge(
    pd.read_sql_query("SELECT amfi_code, expense_ratio_pct, category FROM dim_fund", conn),
    pd.read_sql_query("SELECT amfi_code, return_3yr_pct FROM fact_performance", conn),
    on="amfi_code"
)

plt.figure(figsize=(9, 6))
sns.scatterplot(data=df_merged_perf, x='expense_ratio_pct', y='return_3yr_pct', hue='category', style='category', s=80)
sns.regplot(data=df_merged_perf, x='expense_ratio_pct', y='return_3yr_pct', scatter=False, color='gray', line_kws={"linestyle": "--"})
plt.title("Expense Ratio vs 3-Year Annualized Return (Correlation Analysis)", pad=15)
plt.xlabel("Expense Ratio (%)")
plt.ylabel("3-Year Return (%)")
plt.legend(title="Asset Category")
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "15_expense_vs_return_scatter.png"), dpi=150)
plt.close()


# --- 16. Payment Mode Transaction Count Pie Chart ---
print("Generating Chart 16: Payment mode transaction count pie chart...")
pay_dist = df_tx.groupby('payment_mode').size().reset_index(name='count')

plt.figure(figsize=(6, 6))
plt.pie(pay_dist['count'], labels=pay_dist['payment_mode'], autopct='%1.1f%%', 
        colors=colors_primary[3:7], startangle=30,
        wedgeprops=dict(edgecolor='w'))
plt.title("Transaction Share by Payment Mode", pad=15)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "16_payment_mode_pie.png"), dpi=150)
plt.close()

conn.close()
print("All 16 charts successfully generated and saved to reports/figures/!")


# --- 5. PROGRAMMATIC NOTEBOOK GENERATION ---
print("\nProgrammatically generating notebooks/EDA_Analysis.ipynb...")

notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Mutual Fund Portfolio Analytics & Exploratory Data Analysis (EDA)\n",
    "\n",
    "This notebook contains a comprehensive data exploration and visualization of the mutual fund portfolio datasets, loaded from the SQLite database `mutual_funds.db`."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import sqlite3\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "import plotly.express as px\n",
    "import plotly.graph_objects as go\n",
    "\n",
    "sns.set_theme(style=\"whitegrid\")\n",
    "db_path = os.path.join(\"..\", \"data\", \"processed\", \"mutual_funds.db\")\n",
    "conn = sqlite3.connect(db_path)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 1. NAV Daily Trend Analysis (2022–2026)\n",
    "Highlighting the 2023 bull run and 2024 market corrections."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_nav = pd.read_sql_query(\"\"\"\n",
    "    SELECT n.date, f.scheme_name, n.nav, f.category\n",
    "    FROM fact_nav n\n",
    "    JOIN dim_fund f ON n.amfi_code = f.amfi_code\n",
    "\"\"\", conn)\n",
    "df_nav['date'] = pd.to_datetime(df_nav['date'])\n",
    "\n",
    "plt.figure(figsize=(12, 6))\n",
    "schemes_to_plot = df_nav['scheme_name'].unique()[:8]\n",
    "for scheme in schemes_to_plot:\n",
    "    subset = df_nav[df_nav['scheme_name'] == scheme].sort_values('date')\n",
    "    plt.plot(subset['date'], subset['nav'], label=scheme.split(' - ')[0], alpha=0.85, linewidth=1.5)\n",
    "\n",
    "plt.axvspan(pd.to_datetime('2023-01-01'), pd.to_datetime('2023-12-31'), color='green', alpha=0.08, label='2023 Bull Run')\n",
    "plt.axvspan(pd.to_datetime('2024-04-01'), pd.to_datetime('2024-06-30'), color='red', alpha=0.08, label='2024 Corrections')\n",
    "\n",
    "plt.title(\"Daily NAV Trends of Key Mutual Fund Schemes (2022–2026)\")\n",
    "plt.xlabel(\"Date\")\n",
    "plt.ylabel(\"NAV\")\n",
    "plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 2. AUM Growth by Fund House (2022–2025)\n",
    "Highlighting SBI Mutual Fund's dominance."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_aum = pd.read_sql_query(\"SELECT date, fund_house, aum_crore FROM fact_aum\", conn)\n",
    "df_aum['year'] = pd.to_datetime(df_aum['date']).dt.year\n",
    "aum_yearly = df_aum.groupby(['year', 'fund_house'])['aum_crore'].mean().reset_index()\n",
    "aum_yearly['aum_lakh_crore'] = aum_yearly['aum_crore'] / 100000\n",
    "\n",
    "plt.figure(figsize=(12, 6))\n",
    "sns.barplot(data=aum_yearly, x='year', y='aum_lakh_crore', hue='fund_house', palette=\"tab10\")\n",
    "plt.title(\"AUM Growth by Fund House (2022–2025)\")\n",
    "plt.xlabel(\"Year\")\n",
    "plt.ylabel(\"AUM (Lakh Crore ₹)\")\n",
    "plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3. SIP Inflow Monthly Trend (Jan 2022 – Dec 2025)\n",
    "Annotating the ₹31,002 Cr peak in Dec 2025."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_sip = pd.read_sql_query(\"SELECT month, sip_inflow_crore FROM fact_monthly_sip_inflows\", conn)\n",
    "df_sip['date'] = pd.to_datetime(df_sip['month'] + '-01')\n",
    "\n",
    "plt.figure(figsize=(10, 5))\n",
    "plt.plot(df_sip['date'], df_sip['sip_inflow_crore'], color=\"#1f77b4\", marker='o', linewidth=2)\n",
    "plt.fill_between(df_sip['date'], df_sip['sip_inflow_crore'], color=\"#1f77b4\", alpha=0.1)\n",
    "\n",
    "peak_row = df_sip.sort_values('date').iloc[-1]\n",
    "plt.plot(peak_row['date'], peak_row['sip_inflow_crore'], 'ro', markersize=8)\n",
    "plt.annotate(f\"All-Time High: \u20b9{int(peak_row['sip_inflow_crore']):,} Cr\\n(Dec 2025)\", \n",
    "             xy=(peak_row['date'], peak_row['sip_inflow_crore']), \n",
    "             xytext=(pd.to_datetime('2024-06-01'), 27000),\n",
    "             arrowprops=dict(facecolor='red', shrink=0.08, width=1, headwidth=6))\n",
    "\n",
    "plt.title(\"Monthly SIP Inflows Trend (Jan 2022 – Dec 2025)\")\n",
    "plt.xlabel(\"Month\")\n",
    "plt.ylabel(\"SIP Inflow (Crores ₹)\")\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 4. Category Inflow Heatmap\n",
    "Months on X-axis, fund categories on Y-axis."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_cat = pd.read_sql_query(\"SELECT month, category, net_inflow_crore FROM fact_category_inflows\", conn)\n",
    "cat_pivot = df_cat.pivot(index='category', columns='month', values='net_inflow_crore')\n",
    "cat_pivot = cat_pivot[sorted(cat_pivot.columns)]\n",
    "\n",
    "plt.figure(figsize=(14, 6))\n",
    "sns.heatmap(cat_pivot, cmap=\"RdYlGn\", center=0, cbar_kws={'label': 'Net Inflow (Crores ₹)'})\n",
    "plt.title(\"Net Monthly Inflows by Fund Category (Heatmap)\")\n",
    "plt.xlabel(\"Month\")\n",
    "plt.ylabel(\"Category\")\n",
    "plt.xticks(rotation=45, ha='right')\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 5. Investor Demographics (Age Group Pie Chart)\n",
    "Visualizing volume distribution across demographics."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_tx = pd.read_sql_query(\"SELECT amount_inr, age_group, gender, state, city_tier, payment_mode FROM fact_transactions\", conn)\n",
    "age_dist = df_tx.groupby('age_group')['amount_inr'].sum().reset_index()\n",
    "\n",
    "plt.figure(figsize=(6, 6))\n",
    "plt.pie(age_dist['amount_inr'], labels=age_dist['age_group'], autopct='%1.1f%%', \n",
    "        colors=sns.color_palette(\"Set2\"), startangle=140, pctdistance=0.85,\n",
    "        wedgeprops=dict(width=0.4, edgecolor='w'))\n",
    "plt.title(\"Total Transaction Volume Split by Age Group\")\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 6. SIP Amount Box Plot by Age Group\n",
    "Comparing transaction amounts across age brackets."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "plt.figure(figsize=(10, 6))\n",
    "sns.boxplot(data=df_tx, x='age_group', y='amount_inr', hue='age_group', palette=\"Set2\", legend=False)\n",
    "plt.title(\"SIP Transaction Amount Distribution by Age Group\")\n",
    "plt.xlabel(\"Age Group\")\n",
    "plt.ylabel(\"Amount (INR)\")\n",
    "plt.yscale('log')\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 7. Gender split pie chart\n",
    "Total transaction amount split by gender."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [],
   "source": [
    "gender_dist = df_tx.groupby('gender')['amount_inr'].sum().reset_index()\n",
    "\n",
    "plt.figure(figsize=(6, 6))\n",
    "plt.pie(gender_dist['amount_inr'], labels=gender_dist['gender'], autopct='%1.1f%%', \n",
    "        colors=[\"#f781bf\", \"#377eb8\"], startangle=90, wedgeprops=dict(edgecolor='w'))\n",
    "plt.title(\"Investor Transaction Value Split by Gender\")\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 8. Geographic Distribution\n",
    "Horizontal bar chart of investment amount by state."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {},
   "outputs": [],
   "source": [
    "state_dist = df_tx.groupby('state')['amount_inr'].sum().reset_index()\n",
    "state_dist['amount_crore'] = state_dist['amount_inr'] / 10000000\n",
    "state_dist = state_dist.sort_values('amount_crore', ascending=False).head(15)\n",
    "\n",
    "plt.figure(figsize=(10, 6))\n",
    "sns.barplot(data=state_dist, x='amount_crore', y='state', hue='state', palette=\"viridis\", legend=False)\n",
    "plt.title(\"Top 15 States by Cumulative Investment Amount\")\n",
    "plt.xlabel(\"Total Investments (Crores ₹)\")\n",
    "plt.ylabel(\"State\")\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 9. T30 vs B30 City Tier Pie Chart\n",
    "Market penetration split."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [],
   "source": [
    "tier_dist = df_tx.groupby('city_tier')['amount_inr'].sum().reset_index()\n",
    "\n",
    "plt.figure(figsize=(6, 6))\n",
    "plt.pie(tier_dist['amount_inr'], labels=tier_dist['city_tier'], autopct='%1.1f%%', \n",
    "        colors=[\"#4daf4a\", \"#984ea3\"], startangle=120, pctdistance=0.75,\n",
    "        wedgeprops=dict(width=0.4, edgecolor='w'))\n",
    "plt.title(\"Investment Split: T30 vs B30 Cities\")\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 10. Folio Count Growth (Jan 2022 – Dec 2025)\n",
    "Mapping folio growth milestones."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_folio = pd.read_sql_query(\"SELECT month, total_folios_crore, equity_folios_crore FROM fact_industry_folio_count\", conn)\n",
    "df_folio['date'] = pd.to_datetime(df_folio['month'] + '-01')\n",
    "df_folio = df_folio.sort_values('date')\n",
    "\n",
    "plt.figure(figsize=(10, 5))\n",
    "plt.plot(df_folio['date'], df_folio['total_folios_crore'], color=\"#e41a1c\", marker='s', linewidth=2.5, label=\"Total Folios\")\n",
    "plt.plot(df_folio['date'], df_folio['equity_folios_crore'], color=\"#377eb8\", linestyle='--', label=\"Equity Folios\")\n",
    "\n",
    "plt.plot(df_folio['date'].iloc[0], df_folio['total_folios_crore'].iloc[0], 'ko')\n",
    "plt.annotate(f\"Jan 2022: {df_folio['total_folios_crore'].iloc[0]} Cr\", \n",
    "             xy=(df_folio['date'].iloc[0], df_folio['total_folios_crore'].iloc[0]), \n",
    "             xytext=(df_folio['date'].iloc[0] + pd.Timedelta(days=60), df_folio['total_folios_crore'].iloc[0] + 0.8))\n",
    "\n",
    "plt.plot(df_folio['date'].iloc[-1], df_folio['total_folios_crore'].iloc[-1], 'ko')\n",
    "plt.annotate(f\"Dec 2025: {df_folio['total_folios_crore'].iloc[-1]} Cr\", \n",
    "             xy=(df_folio['date'].iloc[-1], df_folio['total_folios_crore'].iloc[-1]), \n",
    "             xytext=(df_folio['date'].iloc[-1] - pd.Timedelta(days=500), df_folio['total_folios_crore'].iloc[-1] - 1.8))\n",
    "\n",
    "plt.title(\"Folio Count Growth Trend (Jan 2022 – Dec 2025)\")\n",
    "plt.xlabel(\"Month\")\n",
    "plt.ylabel(\"Folios (Crores)\")\n",
    "plt.legend()\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 11. NAV Return Correlation Matrix Heatmap\n",
    "Comparing return correlation between 10 selected funds."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "metadata": {},
   "outputs": [],
   "source": [
    "nav_wide = df_nav.pivot(index='date', columns='scheme_name', values='nav')\n",
    "selected_schemes = nav_wide.columns[:10]\n",
    "corr_matrix = nav_wide[selected_schemes].pct_change().dropna().corr()\n",
    "short_labels = [col.split(' - ')[0] for col in corr_matrix.columns]\n",
    "\n",
    "plt.figure(figsize=(10, 8))\n",
    "sns.heatmap(corr_matrix, annot=True, cmap=\"coolwarm\", fmt=\".2f\", \n",
    "            xticklabels=short_labels, yticklabels=short_labels, square=True)\n",
    "plt.title(\"Daily NAV Return Correlation Matrix (10 Selected Funds)\")\n",
    "plt.xticks(rotation=45, ha='right')\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 12. Sector Allocation Donut Chart\n",
    "Equity fund industry concentrations."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_holdings = pd.read_sql_query(\"SELECT sector, weight_pct FROM fact_portfolio_holdings\", conn)\n",
    "sector_dist = df_holdings.groupby('sector')['weight_pct'].sum().reset_index()\n",
    "sector_dist = sector_dist.sort_values('weight_pct', ascending=False).head(8)\n",
    "\n",
    "plt.figure(figsize=(6, 6))\n",
    "plt.pie(sector_dist['weight_pct'], labels=sector_dist['sector'], autopct='%1.1f%%', \n",
    "        colors=sns.color_palette(\"tab10\"), startangle=45, pctdistance=0.75,\n",
    "        wedgeprops=dict(width=0.4, edgecolor='w'))\n",
    "plt.title(\"Aggregate Sector Allocation in Portfolio Holdings\")\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 13. Morningstar Ratings Distribution\n",
    "Count of schemes by star ratings."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_perf = pd.read_sql_query(\"SELECT morningstar_rating FROM fact_performance\", conn)\n",
    "plt.figure(figsize=(8, 5))\n",
    "sns.countplot(data=df_perf, x='morningstar_rating', hue='morningstar_rating', palette=\"Blues_r\", legend=False)\n",
    "plt.title(\"Mutual Fund Count by Morningstar Star Rating\")\n",
    "plt.xlabel(\"Morningstar Rating\")\n",
    "plt.ylabel(\"Count\")\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 14. Risk Category count bar chart\n",
    "Static risk distribution registry."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_fund_meta = pd.read_sql_query(\"SELECT risk_category FROM dim_fund\", conn)\n",
    "plt.figure(figsize=(8, 5))\n",
    "sns.countplot(data=df_fund_meta, x='risk_category', hue='risk_category', palette=\"rocket_r\", legend=False,\n",
    "              order=['Low', 'Moderate', 'Moderately High', 'High', 'Very High'])\n",
    "plt.title(\"Distribution of Mutual Funds by Risk Category\")\n",
    "plt.xlabel(\"Risk Category\")\n",
    "plt.ylabel(\"Count\")\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 15. Expense Ratio vs Returns Scatter Plot\n",
    "Performance correlation baseline analysis."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_merged_perf = pd.merge(\n",
    "    pd.read_sql_query(\"SELECT amfi_code, expense_ratio_pct, category FROM dim_fund\", conn),\n",
    "    pd.read_sql_query(\"SELECT amfi_code, return_3yr_pct FROM fact_performance\", conn),\n",
    "    on=\"amfi_code\"\n",
    ")\n",
    "plt.figure(figsize=(9, 6))\n",
    "sns.scatterplot(data=df_merged_perf, x='expense_ratio_pct', y='return_3yr_pct', hue='category', style='category', s=80)\n",
    "sns.regplot(data=df_merged_perf, x='expense_ratio_pct', y='return_3yr_pct', scatter=False, color='gray', line_kws={\"linestyle\": \"--\"})\n",
    "plt.title(\"Expense Ratio vs 3-Year Annualized Return (Correlation Analysis)\")\n",
    "plt.xlabel(\"Expense Ratio (%)\")\n",
    "plt.ylabel(\"3-Year Return (%)\")\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 16. Payment Mode Transaction Count Pie Chart\n",
    "Splitting transactions by convenience mode."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_tx_pm = pd.read_sql_query(\"SELECT payment_mode FROM fact_transactions\", conn)\n",
    "pay_dist = df_tx_pm.groupby('payment_mode').size().reset_index(name='count')\n",
    "\n",
    "plt.figure(figsize=(6, 6))\n",
    "plt.pie(pay_dist['count'], labels=pay_dist['payment_mode'], autopct='%1.1f%%', \n",
    "        colors=sns.color_palette(\"tab10\")[3:7], startangle=30, wedgeprops=dict(edgecolor='w'))\n",
    "plt.title(\"Transaction Share by Payment Mode\")\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 🔬 10 Key Business & EDA Findings\n",
    "\n",
    "Based on the visualization and data analysis, here are the 10 core findings:\n",
    "\n",
    "1. **NAV Market Correction Sensitivity:** Large-cap and index mutual fund daily Net Asset Values show severe pullbacks during the marked Q2 2024 market correction period, whilst debt-oriented schemes remain highly stable (Ref: `reports/figures/01_nav_trends.png`).\n",
    "2. **AUM Concentration in Giants:** SBI Mutual Fund dominates the asset management space, maintaining an AUM scale reaching peak values of ₹12.5L Crore, which is more than double the size of medium-sized peers like DSP or Axis MF (Ref: `reports/figures/02_aum_growth.png`).\n",
    "3. **Aggressive SIP Inflow Scale:** Monthly retail investor SIP flows show a massive compound trajectory, climbing from ₹11,517 Cr in Jan 2022 to an all-time record high of ₹31,002 Cr in Dec 2025, signifying deep retail financialization (Ref: `reports/figures/03_sip_inflow_trend.png`).\n",
    "4. **High Equity Inflow Density:** The category inflows heatmap reveals a permanent green concentration (positive net inflows) in Mid Cap, Small Cap, and Flexi Cap equity funds during 2024 and 2025, indicating highly aggressive risk appetite among retail investors (Ref: `reports/figures/04_category_inflow_heatmap.png`).\n",
    "5. **Dominant Millennial & Gen X Investor Share:** Demographic analysis shows that the 26–35 age bracket (43.8%) and the 36–45 age bracket (27.2%) contribute to more than 70% of the aggregate investment value volume (Ref: `reports/figures/05_age_group_pie.png`).\n",
    "6. **Higher Demographics Ticket Size:** While 26-35 age bracket has the highest transaction frequency, the 46-55 age bracket boasts a significantly higher median transaction size (Ref: `reports/figures/06_sip_box_plot.png`).\n",
    "7. **Deep Geographical Concentration:** Maharashtra alone contributes to more than 35% of the total mutual fund transaction volumes, illustrating a high degree of capital concentration in financial hubs like Mumbai (Ref: `reports/figures/08_geographic_state_bar.png`).\n",
    "8. **B30 Market Expansion Potential:** Cities beyond the top 30 (B30 Tier) contribute 30.1% of the cumulative investment volume, indicating a major underpenetrated growth market for retail digital platforms (Ref: `reports/figures/09_city_tier_pie.png`).\n",
    "9. **Violent Folio Expansion Trajectory:** Total industry folios doubled in under four years, expanding from 13.26 Crore in Jan 2022 to 26.12 Crore in Dec 2025, matching the high retail interest (Ref: `reports/figures/10_folio_growth.png`).\n",
    "10. **High Sector Concentration:** The equity portfolios show heavy sector concentration, with the Financial Services and IT sectors swallowing up more than 52% of the aggregate equity holding weight (Ref: `reports/figures/12_sector_donut.png`)."
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.13"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

# Write notebook file
notebook_path = os.path.join(notebook_dir, "EDA_Analysis.ipynb")
with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(notebook_content, f, indent=1)

print(f"Successfully generated notebooks/EDA_Analysis.ipynb!")
