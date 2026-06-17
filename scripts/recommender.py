"""
Bluestock Mutual Fund Cohort Demographic Recommender.
This script implements a content-based recommendation class that takes an investor's ID,
infers their risk profile from demographic age cohorts, and recommends the top 3
highest-rated/performing mutual fund schemes they do not currently own.
"""
import os
import sqlite3
import pandas as pd

# Paths
workspace = r"c:\Datatatatta"
db_path = os.path.join(workspace, "data", "db", "bluestock_mf.db")

class MutualFundRecommender:
    """
    Programmatic recommendation engine for matching investor portfolios
    with suitable fund schemes using age-inferred risk grade rules.
    """
    def __init__(self, db_path):
        """
        Initializes the recommender with the path to the database.
        """
        self.db_path = db_path
        
    def get_conn(self):
        """
        Establishes and returns a connection to the SQLite database.
        """
        return sqlite3.connect(self.db_path)
        
    def recommend_for_investor(self, investor_id):
        """
        Generates up to 3 recommended mutual fund schemes matching the investor's demographic age cohort.
        Excludes schemes they already own.
        """
        conn = self.get_conn()
        
        # 1. Fetch investor demographics and owned funds
        investor_tx = pd.read_sql_query("""
            SELECT t.investor_id, t.age_group, t.gender, t.amfi_code, f.category, f.risk_category
            FROM fact_transactions t
            JOIN dim_fund f ON t.amfi_code = f.amfi_code
            WHERE t.investor_id = ?
        """, conn, params=(investor_id,))
        
        if investor_tx.empty:
            conn.close()
            return f"Investor '{investor_id}' not found in the transaction registry."
            
        age_group = investor_tx['age_group'].iloc[0]
        owned_funds = set(investor_tx['amfi_code'].unique())
        
        # 2. Determine target risk profile based on age group
        # Demographics-based risk mapping rules:
        # - 18-25 / 26-35: Very High / High risk (Equity focus)
        # - 36-45 / 46-55: Moderate / Moderately High risk (Balanced mix)
        # - 56+: Low risk (Debt / Gilt focus)
        if age_group in ['18-25', '26-35']:
            target_categories = ['Equity']
            target_risk_levels = ['Very High', 'High']
        elif age_group in ['36-45', '46-55']:
            target_categories = ['Equity', 'Debt']
            target_risk_levels = ['Moderate', 'Moderately High']
        else:
            target_categories = ['Debt']
            target_risk_levels = ['Low', 'Moderate']
            
        # 3. Query potential recommended funds matching targets
        candidates = pd.read_sql_query("""
            SELECT f.amfi_code, f.scheme_name, f.fund_house, f.category, f.sub_category, f.risk_category, p.sharpe_ratio, p.morningstar_rating
            FROM dim_fund f
            JOIN fact_performance p ON f.amfi_code = p.amfi_code
            ORDER BY p.morningstar_rating DESC, p.sharpe_ratio DESC
        """, conn)
        
        conn.close()
        
        # Filter candidates matching inferred target profile
        matching_candidates = candidates[
            candidates['category'].isin(target_categories) & 
            candidates['risk_category'].isin(target_risk_levels)
        ]
        
        # Exclude funds the investor already owns
        recommendations = matching_candidates[~matching_candidates['amfi_code'].isin(owned_funds)]
        
        # Return top 3 recommendations
        return recommendations.head(3)

if __name__ == "__main__":
    recommender = MutualFundRecommender(db_path)
    
    # Test with a known investor from the transaction logs
    conn = sqlite3.connect(db_path)
    test_investor = conn.execute("SELECT investor_id FROM fact_transactions LIMIT 1").fetchone()[0]
    conn.close()
    
    print(f"Generating fund recommendations for test investor: {test_investor}...")
    recs = recommender.recommend_for_investor(test_investor)
    
    if isinstance(recs, pd.DataFrame):
        print(recs[['scheme_name', 'category', 'risk_category', 'morningstar_rating', 'sharpe_ratio']].to_string(index=False))
    else:
        print(recs)
