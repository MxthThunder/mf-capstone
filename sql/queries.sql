-- Bluestock Mutual Fund Capstone Queries

-- 1. Top 5 Funds by AUM
SELECT 
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    p.aum_crore
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

-- 2. Average NAV per Month for Each Scheme in 2025
SELECT 
    f.scheme_name,
    d.year,
    d.month,
    ROUND(AVG(n.nav), 4) AS avg_nav
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
JOIN dim_date d ON n.date = d.date
WHERE d.year = 2025
GROUP BY f.scheme_name, d.year, d.month
ORDER BY f.scheme_name, d.month;

-- 3. SIP YoY Growth Rate (Monthly Comparison)
SELECT 
    month,
    sip_inflow_crore,
    sip_aum_lakh_crore,
    yoy_growth_pct
FROM fact_monthly_sip_inflows
ORDER BY month;

-- 4. Investor Transactions Volume and Amount Breakdown by State
SELECT 
    state,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr,
    ROUND(AVG(amount_inr), 2) AS avg_transaction_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- 5. Mutual Funds with Expense Ratio < 1.0%
SELECT 
    amfi_code,
    scheme_name,
    fund_house,
    category,
    sub_category,
    plan,
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- 6. Returns Outperformance Rank (Alpha and Net Return 3Yr vs Benchmark)
SELECT 
    f.scheme_name,
    f.fund_house,
    p.return_3yr_pct,
    p.benchmark_3yr_pct,
    ROUND(p.return_3yr_pct - p.benchmark_3yr_pct, 2) AS outperformance_pct,
    p.alpha,
    p.beta
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
ORDER BY outperformance_pct DESC;

-- 7. Average Transaction Size by Age Group and Gender
SELECT 
    age_group,
    gender,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_amount,
    ROUND(AVG(amount_inr), 2) AS avg_amount
FROM fact_transactions
GROUP BY age_group, gender
ORDER BY age_group, gender;

-- 8. Fund House AUM Concentration (Top 3 Fund Houses Share of Total AUM)
WITH aum_totals AS (
    SELECT 
        fund_house,
        SUM(aum_crore) AS house_aum,
        (SELECT SUM(aum_crore) FROM fact_performance) AS total_aum
    FROM fact_performance p
    JOIN dim_fund f ON p.amfi_code = f.amfi_code
    GROUP BY fund_house
)
SELECT 
    fund_house,
    house_aum,
    ROUND((house_aum * 100.0 / total_aum), 2) AS aum_market_share_pct
FROM aum_totals
ORDER BY house_aum DESC
LIMIT 3;

-- 9. High-Value Transactions (> 5 Lakh INR) by KYC Status
SELECT 
    kyc_status,
    COUNT(*) AS high_value_count,
    ROUND(SUM(amount_inr), 2) AS high_value_total,
    ROUND(AVG(amount_inr), 2) AS high_value_avg
FROM fact_transactions
WHERE amount_inr > 500000
GROUP BY kyc_status;

-- 10. Performance Correlation: Average 3-Year Return and Risk Grade by Morningstar Rating
SELECT 
    morningstar_rating,
    COUNT(*) AS scheme_count,
    ROUND(AVG(return_3yr_pct), 2) AS avg_3yr_return,
    ROUND(AVG(sharpe_ratio), 2) AS avg_sharpe_ratio,
    ROUND(AVG(expense_ratio_pct), 2) AS avg_expense_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
GROUP BY morningstar_rating
ORDER BY morningstar_rating DESC;
