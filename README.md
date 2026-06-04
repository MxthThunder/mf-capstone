# Bluestock Mutual Fund Capstone Project

An end-to-end data engineering, processing, risk-return analytics, advanced financial modeling, and dashboard application for mutual fund portfolios. 

This project implements a robust ETL pipeline, loads a star schema SQLite database, executes detailed performance analytics, simulates 5-year NAV growth paths (Monte Carlo), optimizes portfolio weights (Markowitz Efficient Frontier), and serves an interactive Streamlit web dashboard.

---

## 📂 Project Directory Structure

```text
bluestock_mf_capstone/
├── data/
│   ├── raw/               ← original downloaded files & NAV API fetches
│   ├── processed/         ← cleaned, daily forward-filled CSVs & scorecards
│   └── db/                ← bluestock_mf.db (SQLite star schema)
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   ├── 05_advanced_analytics.ipynb  (Monte Carlo B3, Markowitz B4, Cohort)
│   └── Performance_Analytics.ipynb (Daily returns, CAGR, Sharpe ranks)
├── scripts/
│   ├── etl_pipeline.py    ← Core pipeline (ingestion, cleaning, DB loading)
│   ├── live_nav_fetch.py  ← Fetches live NAV from mfapi.in API
│   ├── compute_metrics.py ← Basic metrics calculator
│   ├── recommender.py     ← Demographics risk-matching recommendation engine
│   ├── streamlit_app.py   ← Streamlit multi-page dashboard app (Bonus B2)
│   ├── schedule_etl.py    ← Weekday cron job trigger at 8 PM (Bonus B1)
│   ├── email_generator.py ← Automated HTML email weekly summaries (Bonus B5)
│   ├── generate_pdf_pptx.py ← Report compiler (Platypus PDF & PPTX)
│   └── compute_performance_analytics.py ← Core analytics calculator
├── sql/
│   ├── schema.sql         ← Star Schema DDL CREATE statements (11 tables)
│   └── queries.sql        ← 10 analytical business queries
├── reports/
│   ├── figures/           ← 16+ exported high-resolution PNG plots
│   ├── Final_Report.pdf   ← Publication-quality formatted PDF report
│   ├── Final_Report.md    ← Markdown copy of final report
│   ├── Presentation.pptx  ← Widescreen 16:9 PowerPoint slides
│   └── Presentation.md    ← Slide outlines and script reference
├── requirements.txt       ← Python dependencies
├── fund_scorecard.csv     ← Output of composite scorecard rankings
├── alpha_beta.csv         ← Output of regression metrics vs Nifty 100
├── benchmark_comparison.png ← Plot of top funds vs Nifty indices
└── README.md              ← Project handbook (this file)
```

---

## 🛠️ Prerequisites & Setup

### 1. Requirements
* Python 3.10 or higher
* Recommended virtual environment manager (e.g., `venv` or `conda`)

### 2. Environment Installation
Clone the repository and install dependencies:
```bash
# Install dependencies
pip install -r requirements.txt
```

*Required libraries include: `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`, `sqlalchemy`, `requests`, `scipy`, `jupyter`, `reportlab`, and `python-pptx`.*

---

## 🚀 Execution Guide

### 1. Run Ingestion, Cleaning & Database Loading (ETL)
Processes raw files, forward-fills holiday gaps, validates referential integrity, and builds the database schema:
```bash
python scripts/etl_pipeline.py
```
*Creates the SQLite database file: `data/db/bluestock_mf.db` (which is git-ignored. Schema tracked at `sql/schema.sql`).*

### 2. Compute Performance Metrics & Scorecards
Calculates daily returns, annualizes CAGRs, computes Sharpe and Sortino ratios, performs Nifty 100 regressions (Alpha & Beta), and outputs scorecard metrics:
```bash
python scripts/compute_performance_analytics.py
```
*Generates `fund_scorecard.csv`, `alpha_beta.csv`, and `benchmark_comparison.png` in the project root.*

### 3. Launch Interactive Streamlit Dashboard (Bonus B2)
Starts the 4-page local web application hosting Executive summaries, performance analytics, demographics splitters, and interactive Monte Carlo simulations:
```bash
streamlit run scripts/streamlit_app.py
```

### 4. Compile Publications PDF & Presentation Slides (D7)
Generates the publication-ready final PDF report and widescreen PowerPoint slides:
```bash
python scripts/generate_pdf_pptx.py
```
*Outputs: `reports/Final_Report.pdf` and `reports/Presentation.pptx`.*

### 5. Trigger Automated HTML Performance Email (Bonus B5)
```bash
python scripts/email_generator.py
```

---

## 📐 Analytics Methodology

* **252-Trading Day Year:** Annualized CAGRs and risk metrics are calculated using the 252-trading day convention to match active market cycles rather than 365 calendar days.
* **Sharpe & Sortino Ratios:** Computed using the RBI Repo Rate proxy ($R_f = 6.5\%$). Sortino denominator uses downside standard deviation (negative returns only) to evaluate negative drawdowns.
* **Alpha & Beta:** Evaluated via Ordinary Least Squares (OLS) regression against Nifty 100 daily returns using `scipy.stats.linregress`. Alpha is annualized ($\text{intercept} \times 252$).
* **Fund Scorecard (0–100):** Formulated as a weighted rank percentile composite index:
  $$\text{Score} = 30\% \times \text{CAGR}_{3yr} + 25\% \times \text{Sharpe} + 20\% \times \text{Alpha} + 15\% \times \text{Expense (inv)} + 10\% \times \text{Max DD (inv)}$$

---

## 💡 Implemented Bonus Features

* **B1 — Weekday Scheduler:** Configured via `scripts/schedule_etl.py` to auto-fetch daily NAVs from API every weekday at 8:00 PM.
* **B2 — Streamlit App:** High-aesthetic multi-page app with dynamic data filtering.
* **B3 — Monte Carlo Simulation:** GBM log-normal NAV projections over 5 years (1,260 trading days) mapping expected path and 90% uncertainty bands.
* **B4 — Markowitz Efficient Frontier:** Portfolio weight allocation engine across 5 key large-cap funds.
* **B5 — Weekly Emailer:** Automatically generates and emails weekly performance summaries formatted in structured HTML.
