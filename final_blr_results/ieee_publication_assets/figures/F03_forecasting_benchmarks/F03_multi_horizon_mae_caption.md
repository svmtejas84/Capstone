# Multi-horizon forecasting MAE by protocol

Five forecast horizons; 14,583 saved evaluation pairs per horizon. v2j ST-PIGNN and v2m MLP/TCN used different weather aggregation and are not identical-input architecture ablations. Negative and unfavorable results are retained.

Source artifacts:
- `final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2J_BENCHMARK.csv` (SHA-256 `bdcba74da9e98af6751bb3920490ec20848d548c829c2f928e1c56c02f642fcc`)
- `final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv` (SHA-256 `397c46339c7d7f7a4774161c54197ee6db3aa034f926a059782f5dcb2deb5a18`)

Derived source data: `source_data/F03_forecasting_metrics.csv`.

Regenerate: `python final_blr_results/ieee_publication_assets/scripts/build_assets.py`.
