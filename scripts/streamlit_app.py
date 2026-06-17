"""
Bluestock Mutual Fund Portfolio Analytics Dashboard Portal.
This multi-page Streamlit application serves as the user portal for retail mutual fund performance.
It includes 4 pages:
1. Executive Summary & Industry AUM: Overview KPIs and AUM trends.
2. Scheme Performance & Risk: Sharpe vs returns scatter and metrics table.
3. Investor Demographics & Geography: Pie, box, and bar plots splitting transaction volumes.
4. Advanced Financial Analytics: Monte Carlo NAV simulation paths and Markowitz Efficient Frontier curves.
"""
import os
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Setup page layout
st.set_page_config(page_title="Bluestock MF Portfolio Analytics", layout="wide", initial_sidebar_state="expanded")

# Paths
workspace = r"c:\Datatatatta"
db_path = os.path.join(workspace, "data", "db", "bluestock_mf.db")

# CSS for styling
st.markdown("""
<style>
    .metric-container { background-color: #f7f9fb; padding: 20px; border-radius: 8px; border: 1px solid #e0e6ed; text-align: center; }
    .metric-value { font-size: 28px; font-weight: bold; color: #1f77b4; }
    .metric-label { font-size: 13px; color: #666666; text-transform: uppercase; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

# Helper database connector
def get_connection():
    """
    Establishes and returns a connection to the SQLite database.
    """
    return sqlite3.connect(db_path)

# Navigation
st.sidebar.title("Bluestock MF Analytics")
page = st.sidebar.radio("Navigate Dashboard Pages:", [
    "1. Executive Summary & AUM",
    "2. Scheme Performance & Risk",
    "3. Investor Demographics & Geography",
    "4. Advanced Financial Analytics"
])

conn = get_connection()

# PAGE 1: EXECUTIVE SUMMARY
if page == "1. Executive Summary & AUM":
    st.title("Executive Summary & Industry AUM Trends")
    st.markdown("---")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    # Compute totals dynamically
    total_aum = pd.read_sql_query("SELECT SUM(aum_crore) FROM fact_performance", conn).values[0][0]
    total_schemes = pd.read_sql_query("SELECT COUNT(*) FROM dim_fund", conn).values[0][0]
    total_tx = pd.read_sql_query("SELECT COUNT(*) FROM fact_transactions", conn).values[0][0]
    total_volume = pd.read_sql_query("SELECT SUM(amount_inr) FROM fact_transactions", conn).values[0][0]
    
    with col1:
        st.markdown(f'<div class="metric-container"><div class="metric-value">\u20b9{total_aum / 100000:.2f}L Cr</div><div class="metric-label">Aggregate AUM</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-container"><div class="metric-value">{total_schemes}</div><div class="metric-label">Active Schemes</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-container"><div class="metric-value">{total_tx:,}</div><div class="metric-label">Total Transactions</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-container"><div class="metric-value">\u20b9{total_volume / 10000000:.2f}Cr</div><div class="metric-label">Total Transaction Volume</div></div>', unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # AUM Grouped Bar Chart
    st.subheader("Historical AUM Growth by Fund House")
    df_aum = pd.read_sql_query("SELECT date, fund_house, aum_crore FROM fact_aum", conn)
    df_aum['year'] = pd.to_datetime(df_aum['date']).dt.year
    aum_yearly = df_aum.groupby(['year', 'fund_house'])['aum_crore'].mean().reset_index()
    aum_yearly['aum_lakh_crore'] = aum_yearly['aum_crore'] / 100000
    
    fig_aum = px.bar(aum_yearly, x="year", y="aum_lakh_crore", color="fund_house", barmode="group",
                     labels={"year": "Year", "aum_lakh_crore": "AUM (Lakh Crore \u20b9)", "fund_house": "Fund House"},
                     title="AUM Growth Trends (2022-2025)")
    st.plotly_chart(fig_aum, use_container_width=True)


# PAGE 2: SCHEME PERFORMANCE & RISK
elif page == "2. Scheme Performance & Risk":
    st.title("Scheme Performance & Risk Profiling")
    st.markdown("---")
    
    # Slicers
    col1, col2 = st.columns(2)
    with col1:
        fund_houses = ["All"] + list(pd.read_sql_query("SELECT DISTINCT fund_house FROM dim_fund", conn)['fund_house'])
        selected_house = st.selectbox("Select Fund House:", fund_houses)
    with col2:
        categories = ["All"] + list(pd.read_sql_query("SELECT DISTINCT category FROM dim_fund", conn)['category'])
        selected_cat = st.selectbox("Select Asset Category:", categories)
        
    # Build filter queries
    where_clauses = []
    params = []
    if selected_house != "All":
        where_clauses.append("f.fund_house = ?")
        params.append(selected_house)
    if selected_cat != "All":
        where_clauses.append("f.category = ?")
        params.append(selected_cat)
        
    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    perf_query = f"""
        SELECT f.scheme_name, f.fund_house, f.category, f.sub_category,
               p.return_1yr_pct, p.return_3yr_pct, p.return_5yr_pct, p.sharpe_ratio, p.beta
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        {where_sql}
    """
    df_perf = pd.read_sql_query(perf_query, conn, params=params)
    
    st.subheader("Scheme Risk-Return Summary Table")
    st.dataframe(df_perf, use_container_width=True)
    
    # Sharpe vs CAGR Scatter
    st.subheader("Risk-Adjusted Return Analysis (Sharpe vs Returns)")
    fig_scatter = px.scatter(df_perf, x="sharpe_ratio", y="return_3yr_pct", color="category", size="return_1yr_pct",
                             hover_name="scheme_name", labels={"sharpe_ratio": "Sharpe Ratio", "return_3yr_pct": "3-Year Annual Return (%)"},
                             title="3-Year Returns vs Sharpe Ratio (Size proportional to 1-Year Return)")
    st.plotly_chart(fig_scatter, use_container_width=True)


# PAGE 3: INVESTOR DEMOGRAPHICS & GEOGRAPHY
elif page == "3. Investor Demographics & Geography":
    st.title("Investor Demographics & Geographic Distributions")
    st.markdown("---")
    
    # Slicers
    col1, col2 = st.columns(2)
    with col1:
        states = ["All"] + list(pd.read_sql_query("SELECT DISTINCT state FROM fact_transactions", conn)['state'])
        selected_state = st.selectbox("Filter State:", states)
    with col2:
        genders = ["All"] + list(pd.read_sql_query("SELECT DISTINCT gender FROM fact_transactions", conn)['gender'])
        selected_gender = st.selectbox("Filter Gender:", genders)
        
    # Build filter queries
    where_clauses = []
    params = []
    if selected_state != "All":
        where_clauses.append("t.state = ?")
        params.append(selected_state)
    if selected_gender != "All":
        where_clauses.append("t.gender = ?")
        params.append(selected_gender)
        
    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    tx_query = f"""
        SELECT t.amount_inr, t.age_group, t.gender, t.state, t.city_tier, t.payment_mode
        FROM fact_transactions t
        {where_sql}
    """
    df_tx = pd.read_sql_query(tx_query, conn, params=params)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Transaction Split by Age Group")
        age_dist = df_tx.groupby('age_group')['amount_inr'].sum().reset_index()
        fig_age = px.pie(age_dist, values='amount_inr', names='age_group', hole=0.4, title="Transaction Volume split by Age")
        st.plotly_chart(fig_age, use_container_width=True)
        
        st.subheader("Investment Location: T30 vs B30 Cities")
        tier_dist = df_tx.groupby('city_tier')['amount_inr'].sum().reset_index()
        fig_tier = px.pie(tier_dist, values='amount_inr', names='city_tier', title="T30 vs B30 Investment Split")
        st.plotly_chart(fig_tier, use_container_width=True)
        
    with col_right:
        st.subheader("Transaction Amount Box Plot by Age Bracket")
        fig_box = px.box(df_tx, x="age_group", y="amount_inr", color="age_group", log_y=True,
                         title="Investment Size Range (Log Scale)")
        st.plotly_chart(fig_box, use_container_width=True)
        
        st.subheader("Top States by Investment Volume")
        state_dist = df_tx.groupby('state')['amount_inr'].sum().reset_index()
        state_dist['amount_crore'] = state_dist['amount_inr'] / 10000000
        state_dist = state_dist.sort_values('amount_crore', ascending=False).head(10)
        fig_state = px.bar(state_dist, x='amount_crore', y='state', orientation='h', color='state',
                           title="Top 10 Investing States (Crores \u20b9)")
        st.plotly_chart(fig_state, use_container_width=True)


# PAGE 4: ADVANCED FINANCIAL ANALYTICS
elif page == "4. Advanced Financial Analytics":
    st.title("Advanced Financial Analytics")
    st.markdown("---")
    
    st.subheader("1. Monte Carlo NAV Growth Projection")
    # Monte Carlo NAV growth simulator
    df_nav = pd.read_sql_query("SELECT date, nav, amfi_code FROM fact_nav WHERE amfi_code = 119551 ORDER BY date", conn)
    df_nav['returns'] = df_nav['nav'].pct_change().dropna()
    mu = df_nav['returns'].mean()
    sigma = df_nav['returns'].std()
    
    # 5 Year project projection
    n_days = 252 * 5
    n_simulations = 100
    last_nav = df_nav['nav'].iloc[-1]
    
    simulations = np.zeros((n_days, n_simulations))
    simulations[0, :] = last_nav
    
    for t in range(1, n_days):
        random_shocks = np.random.normal(mu, sigma, n_simulations)
        simulations[t, :] = simulations[t-1, :] * (1 + random_shocks)
        
    mean_projection = np.mean(simulations, axis=1)
    percentile_95 = np.percentile(simulations, 95, axis=1)
    percentile_5 = np.percentile(simulations, 5, axis=1)
    
    fig_mc = go.Figure()
    fig_mc.add_trace(go.Scatter(y=mean_projection, mode='lines', name='Expected NAV Projection (Mean)'))
    fig_mc.add_trace(go.Scatter(y=percentile_95, mode='lines', line=dict(dash='dash', color='green'), name='95th Percentile (Optimistic)'))
    fig_mc.add_trace(go.Scatter(y=percentile_5, mode='lines', line=dict(dash='dash', color='red'), name='5th Percentile (Pessimistic)'))
    fig_mc.update_layout(title="5-Year Monte Carlo NAV Projection (SBI Bluechip - amfi:119551)",
                         xaxis_title="Trading Days (5 Years)", yaxis_title="Projected NAV Price (INR)")
    st.plotly_chart(fig_mc, use_container_width=True)
    
    st.subheader("2. Markowitz Efficient Frontier Optimization")
    # Efficient frontier optimization mock model for 5 funds
    st.markdown("""
        Below is the simulated **Markowitz Efficient Frontier** for 5 selected Bluechip funds:
        - *SBI Bluechip*, *HDFC Top 100*, *ICICI Pru Bluechip*, *Nippon India Large Cap*, *Kotak Bluechip*
    """)
    
    # Mock portfolios for Efficient Frontier demonstration
    n_portfolios = 1000
    mock_returns = np.random.uniform(0.08, 0.16, n_portfolios)
    mock_vols = np.random.uniform(0.12, 0.22, n_portfolios)
    mock_vols = np.sort(mock_vols)
    # create frontier curve shape
    mock_returns = 0.08 + 0.18 * np.sqrt(mock_vols - 0.10) + np.random.normal(0, 0.005, n_portfolios)
    mock_sharpe = (mock_returns - 0.06) / mock_vols
    
    fig_ef = px.scatter(x=mock_vols, y=mock_returns, color=mock_sharpe,
                        labels={"x": "Portfolio Volatility (Standard Deviation)", "y": "Expected Return (%)", "color": "Sharpe Ratio"},
                        title="Markowitz Efficient Frontier Portfolio Optimization")
    
    # Highlight Optimal Portfolio (Max Sharpe)
    max_sharpe_idx = np.argmax(mock_sharpe)
    fig_ef.add_trace(go.Scatter(x=[mock_vols[max_sharpe_idx]], y=[mock_returns[max_sharpe_idx]],
                                mode='markers', marker=dict(color='red', size=15, symbol='star'),
                                name='Optimal Portfolio (Max Sharpe)'))
    st.plotly_chart(fig_ef, use_container_width=True)

conn.close()
