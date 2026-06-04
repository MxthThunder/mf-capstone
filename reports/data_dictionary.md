# Mutual Fund Analytics Database - Data Dictionary

This document serves as the data dictionary and schema documentation for the SQLite processed database `mutual_funds.db`. The database is structured as a **Star Schema** designed for efficient reporting and analytical queries.

---

## 🗺️ Star Schema Architecture

The database is divided into dimensions (prefixed with `dim_`) and fact tables (prefixed with `fact_`):

*   **Dimensions:**
    *   `dim_fund`: Fund registry with static attributes (PK: `amfi_code`).
    *   `dim_date`: Unified calendar for time-series aggregation (PK: `date`).
*   **Facts:**
    *   `fact_nav`: Daily historical Net Asset Values (NAV) for each scheme (FK to fund and date).
    *   `fact_transactions`: Log of investor transactions (FK to fund and date).
    *   `fact_performance`: Historical return, risk, and alpha statistics (FK to fund).
    *   `fact_aum`: Historical Assets Under Management (AUM) by fund house (FK to date).
    *   `fact_monthly_sip_inflows`: Aggregate monthly SIP industry metrics.
    *   `fact_category_inflows`: Aggregate monthly net inflows by mutual fund category.
    *   `fact_industry_folio_count`: Monthly folio registry counts across asset classes.
    *   `fact_benchmark_indices`: Historical closing values for reference benchmark indices (FK to date).
    *   `fact_portfolio_holdings`: Detailed equity security holdings for each scheme (FK to fund and date).

---

## 📑 Table Schema Definitions

### 1. `dim_fund` (Fund Dimension)
*   **Description:** Registered mutual fund schemes and static attributes.
*   **Source Reference:** `01_fund_master.csv`

| Column | Data Type | Key | Nullable | Description |
| :--- | :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | PK | NO | Unique Association of Mutual Funds in India (AMFI) scheme code. |
| `fund_house` | TEXT | - | NO | Name of the asset management company (e.g., SBI Mutual Fund). |
| `scheme_name` | TEXT | - | NO | Official name of the mutual fund scheme. |
| `category` | TEXT | - | NO | Broad asset category class (e.g., Equity, Debt). |
| `sub_category` | TEXT | - | NO | Sub-category of the fund (e.g., Large Cap, Gilt, Mid Cap). |
| `plan` | TEXT | - | NO | Distribution plan type (Regular or Direct). |
| `launch_date` | TEXT | - | YES | Launch date of the scheme formatted as `YYYY-MM-DD`. |
| `benchmark` | TEXT | - | YES | Target index used for performance comparison. |
| `expense_ratio_pct` | REAL | - | YES | Annual fee charged to investors as a percentage of assets. |
| `exit_load_pct` | REAL | - | YES | Fee charged when exiting/redeeming the fund early. |
| `min_sip_amount` | REAL | - | YES | Minimum monthly Systematic Investment Plan (SIP) amount. |
| `min_lumpsum_amount`| REAL | - | YES | Minimum single lumpsum investment amount. |
| `fund_manager` | TEXT | - | YES | Name of the primary portfolio manager. |
| `risk_category` | TEXT | - | YES | Qualitative risk profile classification (e.g., Very High, Moderate).|
| `sebi_category_code`| TEXT | - | YES | SEBI regulatory category code identifier. |

---

### 2. `dim_date` (Date Dimension)
*   **Description:** Calendar dimension populated dynamically from all transaction and time-series dates.
*   **Source Reference:** Generated dynamically during ingestion pipeline.

| Column | Data Type | Key | Nullable | Description |
| :--- | :--- | :--- | :--- | :--- |
| `date` | TEXT | PK | NO | ISO standard date string formatted as `YYYY-MM-DD`. |
| `year` | INTEGER | - | NO | Calendar year (e.g., 2025). |
| `quarter` | INTEGER | - | NO | Calendar quarter (1 through 4). |
| `month` | INTEGER | - | NO | Month of the year (1 through 12). |
| `day` | INTEGER | - | NO | Day of the month (1 through 31). |
| `is_weekend` | INTEGER | - | NO | Boolean flag (1 for Saturday/Sunday, 0 for weekdays). |
| `month_name` | TEXT | - | NO | Full name of the calendar month (e.g., January). |

---

### 3. `fact_nav` (Net Asset Value Fact)
*   **Description:** Daily NAV entries for each mutual fund. Weekends and holidays are forward-filled.
*   **Source Reference:** `02_nav_history.csv`

| Column | Data Type | Key | Nullable | Description |
| :--- | :--- | :--- | :--- | :--- |
| `nav_id` | INTEGER | PK | NO | Auto-incrementing primary key. |
| `amfi_code` | INTEGER | FK | NO | References `dim_fund(amfi_code)`. |
| `date` | TEXT | FK | NO | References `dim_date(date)`. |
| `nav` | REAL | - | NO | Net Asset Value (NAV) price per unit. Must be > 0. |

---

### 4. `fact_transactions` (Investor Transactions Fact)
*   **Description:** Individual transaction log entries showing purchases and redemptions.
*   **Source Reference:** `08_investor_transactions.csv`

| Column | Data Type | Key | Nullable | Description |
| :--- | :--- | :--- | :--- | :--- |
| `transaction_id` | INTEGER | PK | NO | Auto-incrementing primary key. |
| `investor_id` | TEXT | - | NO | Unique obfuscated investor identifier. |
| `transaction_date` | TEXT | FK | NO | References `dim_date(date)`. |
| `amfi_code` | INTEGER | FK | NO | References `dim_fund(amfi_code)`. |
| `transaction_type` | TEXT | - | NO | Type of transaction: `SIP`, `Lumpsum`, or `Redemption`. |
| `amount_inr` | REAL | - | NO | Monetary value of the transaction in INR. Must be > 0. |
| `state` | TEXT | - | YES | State of residence of the investor. |
| `city` | TEXT | - | YES | City of residence of the investor. |
| `city_tier` | TEXT | - | YES | City category tier classification (Tier 1, Tier 2, etc.). |
| `age_group` | TEXT | - | YES | Demographics age bucket (e.g., 18-25, 26-35). |
| `gender` | TEXT | - | YES | Gender of the investor. |
| `annual_income_lakh`| REAL | - | YES | Annual income of the investor in Lakhs INR. |
| `payment_mode` | TEXT | - | YES | Transaction payment mode (UPI, Net Banking, Cheque, Mandate).|
| `kyc_status` | TEXT | - | YES | KYC compliance status (Verified, Pending). |

---

### 5. `fact_performance` (Performance & Risk Fact)
*   **Description:** Return and risk indicators for each mutual fund.
*   **Source Reference:** `07_scheme_performance.csv`

| Column | Data Type | Key | Nullable | Description |
| :--- | :--- | :--- | :--- | :--- |
| `performance_id` | INTEGER | PK | NO | Auto-incrementing primary key. |
| `amfi_code` | INTEGER | FK | NO | References `dim_fund(amfi_code)`. |
| `return_1yr_pct` | REAL | - | YES | 1-year trailing annualized return percentage. |
| `return_3yr_pct` | REAL | - | YES | 3-year trailing annualized return percentage. |
| `return_5yr_pct` | REAL | - | YES | 5-year trailing annualized return percentage. |
| `benchmark_3yr_pct`| REAL | - | YES | 3-year trailing return of the scheme's benchmark. |
| `alpha` | REAL | - | YES | Risk-adjusted return measure vs benchmark index (Alpha). |
| `beta` | REAL | - | YES | Systematic risk volatility factor vs benchmark (Beta). |
| `sharpe_ratio` | REAL | - | YES | Risk-adjusted excess return reward metric. |
| `sortino_ratio` | REAL | - | YES | Downside risk-adjusted return ratio. |
| `std_dev_ann_pct` | REAL | - | YES | Annualized standard deviation volatility percentage. |
| `max_drawdown_pct` | REAL | - | YES | Peak-to-trough maximum percentage decline. |
| `aum_crore` | REAL | - | YES | Assets Under Management in Crores INR. |
| `morningstar_rating`| INTEGER | - | YES | Quality star rating (1 to 5). |
| `risk_grade` | TEXT | - | YES | Risk profile rank designation. |

---

### 6. `fact_aum` (AUM Logs Fact)
*   **Description:** Assets Under Management historical log tracking at the fund house level.
*   **Source Reference:** `03_aum_by_fund_house.csv`

| Column | Data Type | Key | Nullable | Description |
| :--- | :--- | :--- | :--- | :--- |
| `aum_id` | INTEGER | PK | NO | Auto-incrementing primary key. |
| `date` | TEXT | FK | NO | References `dim_date(date)`. |
| `fund_house` | TEXT | - | NO | Name of the fund house. |
| `aum_lakh_crore` | REAL | - | YES | Assets under management in Lakh Crores INR. |
| `aum_crore` | REAL | - | YES | Assets under management in Crores INR. |
| `num_schemes` | INTEGER | - | YES | Active fund counts run by this asset manager. |

---

### 7. `fact_monthly_sip_inflows` (SIP Inflows Fact)
*   **Description:** Monthly aggregated Systematic Investment Plan inflows into the industry.
*   **Source Reference:** `04_monthly_sip_inflows.csv`

| Column | Data Type | Key | Nullable | Description |
| :--- | :--- | :--- | :--- | :--- |
| `month` | TEXT | PK | NO | Format `YYYY-MM`. |
| `sip_inflow_crore` | REAL | - | YES | Monthly SIP collections in Crores INR. |
| `active_sip_accounts_crore`| REAL | - | YES | Outstanding active SIP account count (in Crores). |
| `new_sip_accounts_lakh`| REAL | - | YES | New SIP registrations in this month (in Lakhs). |
| `sip_aum_lakh_crore`| REAL | - | YES | Total assets built via SIP investments (Lakh Crores). |
| `yoy_growth_pct` | REAL | - | YES | Year-over-Year growth percentage of monthly inflows. |

---

### 8. `fact_category_inflows` (Category Inflows Fact)
*   **Description:** Aggregated net inflows per mutual fund category.
*   **Source Reference:** `05_category_inflows.csv`

| Column | Data Type | Key | Nullable | Description |
| :--- | :--- | :--- | :--- | :--- |
| `category_inflow_id`| INTEGER | PK | NO | Auto-incrementing primary key. |
| `month` | TEXT | - | NO | Month identifier formatted as `YYYY-MM`. |
| `category` | TEXT | - | NO | Fund category name. |
| `net_inflow_crore` | REAL | - | YES | Net new money inflows/outflows in Crores INR. |

---

### 9. `fact_industry_folio_count` (Folio Count Fact)
*   **Description:** Industry-wide mutual fund folder folio counts.
*   **Source Reference:** `06_industry_folio_count.csv`

| Column | Data Type | Key | Nullable | Description |
| :--- | :--- | :--- | :--- | :--- |
| `month` | TEXT | PK | NO | Format `YYYY-MM`. |
| `total_folios_crore`| REAL | - | YES | Aggregate folder folios count (in Crores). |
| `equity_folios_crore`| REAL | - | YES | Folios in equity funds. |
| `debt_folios_crore` | REAL | - | YES | Folios in debt funds. |
| `hybrid_folios_crore`| REAL | - | YES | Folios in hybrid asset allocation schemes. |
| `others_folios_crore`| REAL | - | YES | Folios in other schemes (Index, Gold, ETFs, Fund of Funds). |

---

### 10. `fact_benchmark_indices` (Benchmark closing prices Fact)
*   **Description:** Daily historical benchmark close levels.
*   **Source Reference:** `10_benchmark_indices.csv`

| Column | Data Type | Key | Nullable | Description |
| :--- | :--- | :--- | :--- | :--- |
| `benchmark_id` | INTEGER | PK | NO | Auto-incrementing primary key. |
| `date` | TEXT | FK | NO | References `dim_date(date)`. |
| `index_name` | TEXT | - | NO | Index identifier name (e.g., NIFTY50, NIFTY 100 TRI). |
| `close_value` | REAL | - | YES | Daily closing value of the benchmark index. |

---

### 11. `fact_portfolio_holdings` (Portfolio Holdings Fact)
*   **Description:** Stock allocation weights of each mutual fund scheme.
*   **Source Reference:** `09_portfolio_holdings.csv`

| Column | Data Type | Key | Nullable | Description |
| :--- | :--- | :--- | :--- | :--- |
| `holding_id` | INTEGER | PK | NO | Auto-incrementing primary key. |
| `amfi_code` | INTEGER | FK | NO | References `dim_fund(amfi_code)`. |
| `stock_symbol` | TEXT | - | NO | Exchange ticker ticker symbol (e.g., HDFCBANK). |
| `stock_name` | TEXT | - | NO | Company name of the equity security. |
| `sector` | TEXT | - | YES | Industrial economic sector classification. |
| `weight_pct` | REAL | - | YES | Weight of this stock in the fund's total portfolio. |
| `market_value_cr` | REAL | - | YES | Market value of the holding in Crores INR. |
| `current_price_inr` | REAL | - | YES | Trading price of the single stock in INR. |
| `portfolio_date` | TEXT | FK | YES | References `dim_date(date)`. |
