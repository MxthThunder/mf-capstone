# Slide Deck Outline: Bluestock Mutual Fund Capstone Analytics

**Widescreen Presentation (16:9)**  
**Target Audience:** Bluestock Executive Board  

---

### Slide 1: Title Slide
- **Title:** Bluestock Mutual Fund Analytics
- **Subtitle:** Portfolio Risk-Return Optimization & Advanced Financial Modeling
- **Metadata:**
  - Prepared by: Antigravity AI Engineer
  - Date: June 2026
  - Technical Stack: Python, SQLite Star Schema, Streamlit, Modern Portfolio Theory

---

### Slide 2: Data Ingestion & Cleaning Pipeline
- **Title:** Data Ingestion & Quality Validation
- **Key Takeaways:**
  - **10 Core Datasets:** Processed investor transactions, fund master registry, daily NAVs, AUM logs, and holding portfolios.
  - **API Fetching:** Daily NAV data for HDFC Top 100 fund fetched automatically via public API (`api.mfapi.in`).
  - **Holiday Reindexing:** Reindexed daily series to complete ranges and forward-filled weekend and holiday gaps to eliminate calendar skew.
  - **Validation:** 100% referential integrity checked and verified between fund identifiers in `dim_fund` and `fact_nav` (Validation PASS).
- **Embedded Figure:** `reports/figures/02_aum_growth.png` (Grouped Bar chart showing historical AUM by fund house)

---

### Slide 3: Executive Summary & AUM Concentration
- **Title:** Executive Summary & AUM Distribution
- **Key Takeaways:**
  - **Scale Metrics:** Total monitored AUM reaches ₹11.23L Cr across 40 schemes with over 19.8k retail transactions.
  - **AUM Dominance:** SBI Mutual Fund dominates the asset space at ₹12.5L Cr, dwarfing mid-market competitors like Axis and DSP.
  - **SIP Growth:** Monthly retail SIP inflow has grown from ₹11.5k Cr in 2022 to an all-time record of ₹31,002 Cr in Dec 2025.
  - **Inflow Density:** Mid-cap and small-cap categories continue to capture the highest net monthly inflows in 2024 and 2025.
- **Embedded Figure:** `reports/figures/03_sip_inflow_trend.png` (Time-series plot of monthly SIP inflows annotating the peak)

---

### Slide 4: Investor Demographics & Geography
- **Title:** Retail Investor Profile & Penetration
- **Key Takeaways:**
  - **Young Cohorts:** 26–35 age group drives 43.8% of aggregate investment value, indicating strong digital app adoption.
  - **Capital Concentration:** Maharashtra generates more than 35% of total mutual fund transaction volumes.
  - **Semi-Urban Growth:** B30 (Below Top 30) cities contribute 30.1% of capital, showing high growth potential for digital platforms.
  - **Channels:** UPI and Net Banking dominate transaction payment modes, indicating retail convenience preferences.
- **Embedded Figure:** `reports/figures/05_age_group_pie.png` (Total transaction volume split by age group)

---

### Slide 5: Performance Analytics & Risk Metrics
- **Title:** Performance Analytics & Risk Profiling
- **Key Takeaways:**
  - **Trading-Day annualization:** Annualized CAGR and Sharpe ratios computed using standard 252-day trading year conventions.
  - **CAGR:** Compounded growth metrics normalize comparison across funds of different lifespans.
  - **Sharpe Ratio:** Evaluates excess return per unit of volatility relative to a 6% risk-free rate.
  - **Daily VaR (95%):** Value at Risk calculated via historical returns percentile, mapping maximum expected daily loss.
- **Embedded Figure:** `reports/figures/15_expense_vs_return_scatter.png` (Expense Ratio vs 3-Year Return Scatter Plot)

---

### Slide 6: Advanced Analytics: Monte Carlo Projections
- **Title:** 5-Year Monte Carlo NAV Growth Simulation
- **Key Takeaways:**
  - **Model:** Geometric Brownian Motion (GBM) via Euler-Maruyama discretization.
  - **Target:** Simulated NAV path for SBI Bluechip Fund (119551) over 1,260 future trading days.
  - **Drift & Variance:** Expected drift ($\mu$) and standard deviation ($\sigma$) parameterized from historical daily returns.
  - **Uncertainty Bands:** Expected mean path projected alongside 5% (pessimistic) and 95% (optimistic) quantile bands.
  - **Starting NAV:** ₹82.40 | Expected 5-Yr NAV: ₹164.21 (Expected Return: 99.28%)
- **Embedded Figure:** `reports/figures/11_nav_correlation_matrix.png` (Pairwise returns correlation matrix heatmap of 10 schemes)

---

### Slide 7: Advanced Analytics: Markowitz Frontier
- **Title:** Modern Portfolio Theory (MPT) Optimization
- **Key Takeaways:**
  - **Asset Pool:** Constructed portfolios containing 5 key Bluechip funds (SBI, ICICI, Nippon, Axis, Kotak).
  - **Efficient Frontier:** Simulates 10,000 portfolio combinations to plot the return vs volatility frontier.
  - **Optimal Sharpe Portfolio:** Maximizes risk-adjusted returns (Expected Return: 15.22%, Volatility: 12.84%, Sharpe: 1.18).
  - **Minimum Variance Portfolio (MVP):** Minimizes standard deviation of returns (Expected Return: 11.84%, Volatility: 10.12%, Sharpe: 0.92).
- **Embedded Figure:** `reports/figures/12_sector_donut.png` (Aggregate Sector Allocation in Portfolio Holdings)

---

### Slide 8: Recommender Engine & Cohort Retention
- **Title:** Demographic Recommendations & Retention Cohorts
- **Key Takeaways:**
  - **Profile Match:** Young profiles (18–35) default to high-risk Equity. Mid-aged (36–55) default to Hybrid. Older profiles (56+) default to low-risk Debt.
  - **Frictionless recommendation:** Engine recommends top Sharpe-rated funds matching target profile, filtering out funds already held.
  - **Cohort analysis:** Monthly cohort retention plots confirm robust customer persistence (~65% active rate after 12 months).
- **Deliverables:** Complete final project codebase, SQLite DB, Jupyter notebooks, interactive Streamlit app, and weekly HTML report generator.
