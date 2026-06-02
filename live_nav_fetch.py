import os
import requests
import pandas as pd

RAW_DIR = os.path.join("data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

BASE_URL = "https://api.mfapi.in/mf"  # public mutual fund API for India [web:2][web:9]

def fetch_nav(scheme_code: str, scheme_name: str):
    url = f"{BASE_URL}/{scheme_code}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    # data["data"] is usually a list of dicts with "date" and "nav" [web:2][web:12]
    nav_list = data.get("data", [])
    df = pd.DataFrame(nav_list)
    out_path = os.path.join(RAW_DIR, f"{scheme_name}_nav.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved {scheme_name} NAV to {out_path}")

if __name__ == "__main__":
    # Example: HDFC Top 100 Direct (125497)
    fetch_nav("125497", "HDFC_Top_100_Direct")
