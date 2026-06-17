# Bluestock Mutual Fund Analytics Capstone Project

An end-to-end data engineering, database loading, risk-return financial modeling, and visual reporting portal for retail mutual fund portfolios. 

This project implements a unified ETL pipeline, loads a SQLite relational star schema database, executes daily returns and risk evaluations, models future expected trajectories (Geometric Brownian Motion Monte Carlo), optimizes asset weight allocations (Markowitz Efficient Frontier), and serves an interactive Streamlit web dashboard.

---

## 📂 Project Directory Structure

```text
bluestock_mf_capstone/
├── data/
│   ├── raw/               ← Ingested raw source CSVs & live API NAV fetches
│   ├── processed/         ← Cleaned daily filled CSVs & scorecard outputs
│   └── db/                ← SQLite relational database (bluestock_mf.db)
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   └── 05_advanced_analytics.ipynb   ← VaR, Monte Carlo, and Markowitz weights
├── scripts/
│   ├── etl_pipeline.py     ← Cleans CSV files and loads SQLite DB schema
│   ├── live_nav_fetch.py   ← Fetches daily NAV prices from api.mfapi.in
│   ├── compute_metrics.py  ← Annualizes CAGR, Sharpe, Beta, and VaR
│   ├── recommender.py      ← Demographic risk-matching CLI engine
│   ├── streamlit_app.py    ← Multi-page interactive Streamlit dashboard
│   ├── schedule_etl.py     ← Weekday cron scheduler trigger at 8 PM
│   ├── email_generator.py  ← Weekly HTML performance digest emailer
│   └── generate_pdf_pptx.py ← Compiles the final PDF report and slide deck
├── sql/
│   ├── schema.sql          ← Database relational Star Schema DDL
│   └── queries.sql         ← Core business analytics query repository
├── reports/
│   ├── figures/            ← 17 exported high-resolution figures
│   ├── Final_Report.pdf    ← 20-page professional ReportLab final PDF report
│   ├── Final_Report.md     ← Markdown text outline of final report
│   └── Bluestock_MF_Presentation.pptx  ← 12-slide PowerPoint presentation
├── requirements.txt        ← Python dependencies
├── run_pipeline.py         ← Master orchestrator pipeline execution script
├── Final_Report.pdf        ← Root copy of the final PDF report
├── Bluestock_MF_Presentation.pptx  ← Root copy of the presentation slide deck
└── README.md               ← Capstone handbook (this file)
```

---

## 🛠️ Prerequisites & Local Setup

### 1. Requirements
* Python 3.10 or higher
* Recommended virtual environment manager (`venv`)

### 2. Environment Installation
Clone the repository and install project dependencies inside a virtual environment:
```bash
# Initialize and activate virtual environment
python -m venv .venv
.venv\Scripts\activate      # On Windows
source .venv/bin/activate    # On Unix/macOS

# Install dependencies
pip install -r requirements.txt
```
*Key packages include: `pandas`, `numpy`, `matplotlib`, `seaborn`, `sqlalchemy`, `requests`, `scipy`, `streamlit`, `python-pptx`, and `reportlab`.*

---

## 📂 Source Dataset Descriptions

The pipeline ingests 10 raw CSV source files located under `data/raw/` to construct the analytics database:

1. **`01_fund_master.csv`**: Fund registry holding static parameters of the 40 mutual fund schemes (amfi_code, category, sub-category, expense ratio, exit load, minimum investments, risk category).
2. **`02_nav_history.csv`**: Daily net asset value (NAV) price time series from 2022 to 2026 for all 40 schemes (39,512 rows).
3. **`03_aum_by_fund_house.csv`**: Historical quarterly Assets Under Management (AUM) logged per AMC.
4. **`04_monthly_sip_inflows.csv`**: Industry-wide monthly aggregate SIP inflows, active account volumes, and YoY growth percentages.
5. **`05_category_inflows.csv`**: Net monthly capital flows across different scheme categories (Equity, Debt, Hybrid).
6. **`06_industry_folio_count.csv`**: Historical monthly folio counts across different mutual fund categories.
7. **`07_scheme_performance.csv`**: Historical pre-calculated scheme CAGRs, Sharpe ratios, and Morningstar ratings.
8. **`08_investor_transactions.csv`**: Micro-ledger containing 19,890 retail investor transaction rows (amount, type, state, city tier, age, gender, KYC, payment mode).
9. **`09_portfolio_holdings.csv`**: Equity asset allocations and sector weights held by each equity fund (371 stock allocation weights).
10. **`10_benchmark_indices.csv`**: Daily index close prices of benchmark indices (Nifty 50, Nifty Midcap 100, Nifty Smallcap 250) from 2022 to 2026.

---

## 🚀 Execution Guide

### 1. Master Pipeline Execution (Recommended)
You can run the entire pipeline—from fetching live API data, cleaning files, loading the database, calculating metrics, and compiling documents—using the master script:
```bash
python run_pipeline.py
```
*Executes all steps sequentially and copies final PDFs and presentations to the root directory.*

### 2. Step-by-Step Script Execution

#### Step 1: Live NAV Ingestion
Fetches latest daily NAV data from the api.mfapi.in service:
```bash
python scripts/live_nav_fetch.py
```

#### Step 2: Database Ingestion & ETL Load
Cleans raw source files, resolves calendar holiday gaps, standardizes transactions, and builds the SQLite relational database `data/db/bluestock_mf.db` using the schema DDL:
```bash
python scripts/etl_pipeline.py
```

#### Step 3: Compute Performance Metrics
Calculates annualized CAGR, Sharpe ratios (6% Rf), Beta, and 95% Daily VaR:
```bash
python scripts/compute_metrics.py
```

#### Step 4: Launch Streamlit Dashboard App
Run the interactive dashboard portal locally:
```bash
streamlit run scripts/streamlit_app.py
```
*Streamlit dashboard serves 4 interactive pages: Executive Summary, Fund Scorecard, Demographics Analytics, and Monte Carlo/Efficient Frontier projections.*

#### Step 4b: Live Published Dashboard (Optional)
The dashboard can be published to Tableau Public or Power BI Service. Once published, the web version can be accessed here:
* **Tableau Public Dashboard:** [Insert Live Dashboard URL Here]

#### Step 5: Compile Final Reports & PowerPoint Slides
Compiles the ReportLab PDF report and the widescreen 16:9 presentation:
```bash
python scripts/generate_pdf_pptx.py
```

#### Step 6: Demographic Recommendation CLI
Test the fund recommendation engine using the command line:
```bash
python recommender.py High
```
*Options for risk appetite: Low, Moderate, High.*

---

## 📈 Advanced Financial Modeling Summary

* **Annualization Convention:** In accordance with professional standards, CAGR and standard deviation parameters are annualized using **252 trading days per year** to prevent calendar bias.
* **Monte Carlo Simulations:** Euler-Maruyama discretization of Geometric Brownian Motion (GBM) is applied to project the expected NAV price path and 90% confidence bands over a 5-year horizon.
* **Markowitz Efficient Frontier:** Uses daily returns covariances across 5 bluechip funds to simulate 10,000 weight allocations, identifying the Maximum Sharpe Tangency Portfolio and the Minimum Variance Portfolio.
* **Sector Concentration (HHI):** Measures portfolio diversification using the Herfindahl-Hirschman Index $HHI = \sum w_i^2$ across sector holdings.
