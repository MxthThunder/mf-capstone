"""
Bluestock Mutual Fund Portfolio Demographics Recommender CLI.
This script provides a command-line interface to get fund recommendations
based on user-specified risk appetite (Low, Moderate, High).
It retrieves the top 3 performing schemes by Sharpe ratio from the SQLite database.
"""
import os
import sys
import sqlite3
import pandas as pd

def get_db_connection():
    """
    Establishes and returns a connection to the SQLite database.
    Looks for the database at canonical workspace paths.
    """
    # Attempt to locate the SQLite database
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "data", "db", "bluestock_mf.db")
    
    if not os.path.exists(db_path):
        # Try relative paths from current working directory
        db_path = os.path.join("data", "db", "bluestock_mf.db")
        
    if not os.path.exists(db_path):
        print(f"Error: Database not found at '{db_path}'. Please ensure the ETL pipeline has run.")
        sys.exit(1)
        
    return sqlite3.connect(db_path)

def get_recommendations(risk_appetite):
    """
    Retrieves the top 3 recommended mutual fund schemes matching the user's risk appetite.
    - Low risk maps to Low risk grade
    - Moderate risk maps to Moderate and Moderately High risk grades
    - High risk maps to High and Very High risk grades
    """
    risk_appetite = risk_appetite.strip().title()
    
    # Map risk appetite to database risk grades
    risk_map = {
        'Low': ['Low'],
        'Moderate': ['Moderate', 'Moderately High'],
        'High': ['High', 'Very High']
    }
    
    if risk_appetite not in risk_map:
        print(f"Error: Invalid risk appetite '{risk_appetite}'. Must be one of: Low, Moderate, High.")
        sys.exit(1)
        
    grades = risk_map[risk_appetite]
    conn = get_db_connection()
    
    # Fetch top 3 funds by Sharpe ratio within matching risk grade
    query = """
        SELECT f.amfi_code, f.scheme_name, p.risk_grade, p.sharpe_ratio
        FROM dim_fund f
        JOIN fact_performance p ON f.amfi_code = p.amfi_code
        WHERE p.risk_grade IN ({})
        ORDER BY p.sharpe_ratio DESC
        LIMIT 3
    """.format(','.join(['?'] * len(grades)))
    
    df = pd.read_sql_query(query, conn, params=grades)
    conn.close()
    
    return df

def print_table(df, title):
    """
    Prints the recommended funds in a nicely formatted CLI table.
    """
    print("\n" + "=" * 80)
    print(f" {title.upper()} ".center(80, "="))
    print("=" * 80)
    
    if df.empty:
        print("No recommendations found.")
        return
        
    # Format columns for display
    print(f"{'AMFI Code':<12} | {'Scheme Name':<45} | {'Risk Grade':<15} | {'Sharpe Ratio':<12}")
    print("-" * 80)
    for _, row in df.iterrows():
        print(f"{row['amfi_code']:<12} | {row['scheme_name'][:45]:<45} | {row['risk_grade']:<15} | {row['sharpe_ratio']:<12.4f}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    # Check if argument is passed
    if len(sys.argv) > 1:
        appetite = sys.argv[1]
    else:
        print("Welcome to the Bluestock Mutual Fund Recommender!")
        print("Available risk appetites: Low, Moderate, High")
        appetite = input("Enter your risk appetite: ")
        
    try:
        recs = get_recommendations(appetite)
        print_table(recs, f"Top 3 Recommendations ({appetite} Risk)")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
