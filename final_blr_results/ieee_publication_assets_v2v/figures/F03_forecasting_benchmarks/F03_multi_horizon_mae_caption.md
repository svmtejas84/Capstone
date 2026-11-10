# Multi-horizon forecasting MAE by protocol

Five horizons and 14,583 saved pairs per horizon in the retrospective centered-weather panel; MLP/TCN use a separate forecast-cutoff-safe feature protocol. These are not identical-input architecture ablations. The full 17-variant inventory is provided separately; unfavorable results are retained.

Source artifacts:
- `final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2J_BENCHMARK.csv` (SHA-256 `bdcba74da9e98af6751bb3920490ec20848d548c829c2f928e1c56c02f642fcc`)
- `final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv` (SHA-256 `397c46339c7d7f7a4774161c54197ee6db3aa034f926a059782f5dcb2deb5a18`)

Derived source data: `source_data/F03_forecasting_metrics.csv`.

Regenerate: `python final_blr_results/ieee_publication_assets_v2v/scripts/build_assets.py`.
