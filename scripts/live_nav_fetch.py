import os
import requests
import pandas as pd

RAW_DIR = os.path.join("data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

BASE_URL = "https://api.mfapi.in/mf"

def fetch_nav(scheme_code: str, scheme_name: str):
    """
    Fetches daily net asset values (NAV) for a specified AMFI scheme code from the public API
    and saves the time series as a raw CSV in data/raw.
    """
    url = f"{BASE_URL}/{scheme_code}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    nav_list = data.get("data", [])
    df = pd.DataFrame(nav_list)
    out_path = os.path.join(RAW_DIR, f"{scheme_name}_nav.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved {scheme_name} NAV to {out_path}")


if __name__ == "__main__":
    schemes = {
        "125497": "HDFC_Top_100_Direct",
        "119551": "SBI_Bluechip",
        "120503": "ICICI_Bluechip",
        "118632": "Nippon_Large_Cap",
        "119092": "Axis_Bluechip",
        "120841": "Kotak_Bluechip"
    }
    
    for code, name in schemes.items():
        try:
            fetch_nav(code, name)
        except Exception as e:
            print(f"Error fetching {name} ({code}): {e}")
