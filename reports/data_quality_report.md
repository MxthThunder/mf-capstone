# Data Quality Report - Day 1 Ingestion

This report outlines the results of the initial data profiling, exploration, and validation check for the Mutual Fund Capstone project.

## 📂 Dataset File Profiles

| Dataset | Shape | Total Nulls | Keys & Target Columns |
| :--- | :--- | :--- | :--- |
| `01_fund_master.csv` | (40, 15) | 0 | `amfi_code` (Primary Key), `fund_house`, `scheme_name` |
| `02_nav_history.csv` | (46000, 3) | 0 | `amfi_code`, `date`, `nav` |
| `03_aum_by_fund_house.csv` | (90, 5) | 0 | `date`, `fund_house`, `aum_lakh_crore` |
| `04_monthly_sip_inflows.csv` | (48, 6) | 12 | `month`, `sip_inflow_crore`, `yoy_growth_pct` |
| `05_category_inflows.csv` | (144, 3) | 0 | `month`, `category`, `net_inflow_crore` |
| `06_industry_folio_count.csv` | (21, 6) | 0 | `month`, `total_folios_crore` |
| `07_scheme_performance.csv` | (40, 19) | 0 | `amfi_code`, `return_3yr_pct`, `sharpe_ratio` |
| `08_investor_transactions.csv` | (32778, 13) | 0 | `investor_id`, `transaction_date`, `amfi_code` |
| `09_portfolio_holdings.csv` | (322, 8) | 0 | `amfi_code`, `stock_symbol`, `weight_pct` |
| `10_benchmark_indices.csv` | (8050, 3) | 0 | `date`, `index_name`, `close_value` |

---

## 🔍 Fund Master Exploration

* **Unique Fund Houses (10):**
  `SBI Mutual Fund`, `HDFC Mutual Fund`, `ICICI Prudential MF`, `Nippon India MF`, `Kotak Mahindra MF`, `Axis Mutual Fund`, `Aditya Birla Sun Life MF`, `UTI Mutual Fund`, `Mirae Asset MF`, `DSP Mutual Fund`
* **Unique Categories (2):**
  `Equity`, `Debt`
* **Unique Sub-Categories (12):**
  `Large Cap`, `Small Cap`, `Gilt`, `Mid Cap`, `Short Duration`, `Value`, `Liquid`, `Index/ETF`, `Flexi Cap`, `Index`, `Large & Mid Cap`, `ELSS`
* **Unique Risk Categories (5):**
  `Moderate`, `Very High`, `Low`, `High`, `Moderately High`

---

## 🔬 AMFI Code Validation
We cross-referenced `amfi_code` values between `01_fund_master.csv` (schema definition) and `02_nav_history.csv` (NAV time series) to verify data integrity:

* Unique codes in `01_fund_master.csv`: **40**
* Unique codes in `02_nav_history.csv`: **40**
* Codes in `fund_master` missing in `nav_history`: **0** (Expected 0)
* Codes in `nav_history` missing in `fund_master`: **0** (Expected 0)

> [!NOTE]
> **Validation Result:** **PASS**. There is a perfect 1:1 foreign key match between `amfi_code` identifiers in the fund master registry and the historical NAV log.

---

## ⚠️ Data Quality Anomalies

- **04_monthly_sip_inflows.csv**: `yoy_growth_pct` column has 12 missing value(s).

* **Anomaly Explanation:**
  The `yoy_growth_pct` column in `04_monthly_sip_inflows.csv` contains **12 missing values** in the first 12 months (all rows of 2022). This is a normal mathematical limitation rather than a data quality error, because the dataset starts in `2022-01` and lacks the prior-year (2021) baseline data necessary to calculate the YoY growth rate.
