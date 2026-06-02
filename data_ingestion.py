import os
import pandas as pd

RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")

def load_csvs():
    csv_files = [f for f in os.listdir(RAW_DIR) if f.endswith(".csv")]
    datasets = {}
    for file in csv_files:
        path = os.path.join(RAW_DIR, file)
        df = pd.read_csv(path)
        print(f"\n=== {file} ===")
        print("shape:", df.shape)
        print("dtypes:")
        print(df.dtypes)
        print("head():")
        print(df.head())
        datasets[file] = df
    return datasets

if __name__ == "__main__":
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    load_csvs()
