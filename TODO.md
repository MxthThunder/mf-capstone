# TODO - Bluestock MF Capstone cleanup

- [x] Delete unwanted automation screenshot files (root-level `pbi_*.png`, `current_screen.png`, `screenshot.png`, and root `benchmark_comparison.png`).
- [x] Remove duplicate/extra notebook and CSV files:
  - [x] Delete `datasetsssss.ipynb` (root)
  - [x] Delete `01_fund_master.csv` (root)
  - [x] Delete `notebooks/EDA_Analysis.ipynb` and `notebooks/Performance_Analytics.ipynb`
- [x] Move generated outputs into canonical locations:
  - [x] Move `alpha_beta.csv` -> `data/processed/alpha_beta.csv`
  - [x] Move `fund_scorecard.csv` -> `data/processed/fund_scorecard.csv`
  - [x] Move `benchmark_comparison.png` -> `reports/figures/benchmark_comparison.png` (it already existed there)
- [x] Verify final folder structure matches the target layout.
- [x] Run a quick sanity check (file existence checks).
