**Final Evaluation Methodology — ST-PIGNN Scaler Evaluation**

This document contains the methodologies executed and exact metrics/tables produced during evaluation. Recommendations and deployment rules have been removed per request.

Overview

- `TARGET_SCALE = 342.9356` (used to convert normalized outputs to µg/m³)
- `TARGET_PM25_MAX = 120.0` (clipping applied when converting to µg/m³)


Methodologies executed

1) Baseline (global target scale)

- Convert model normalized outputs to µg/m³ via `pred_ug = pred_norm * TARGET_SCALE` and clip to `TARGET_PM25_MAX`.
- Compute aggregate metrics (MAE, MSE, RMSE) on evaluation sets in both normalized and µg units.

Baseline target-scale metrics (holdout)

These are the metrics when applying only the constant `TARGET_SCALE` to model outputs (no per-zone correction). Values computed on the holdout run (n=1000):

| metric | normalized | µg/m³ |
|--------|-----------:|------:|
| MAE    | 0.05899714910509174 | 20.23222272664410 |
| MSE    | 0.00615472117671275 | 723.82491151088900 |
| RMSE   | 0.07845203105537005 | 26.90399434119196 |


2) Per-zone linear correction (offline)

- Fit `obs = a * raw_pred + b` per `zone_id` using paired samples in µg units (least-squares). Implemented in `scripts/fit_scalers.py`.
- Two fitting scopes used:
	- ``per_zone`` fit on the full calibration CSV (initial run that contained leakage)
	- ``per_zone`` fit on training-only CSV (training pairs = calibration minus holdout rows), used for honest holdout evaluation

3) Holdout evaluation

- Generate holdout pairs with `scripts/generate_holdout_pairs.py` (recent `holdout_hours`, capped by `--max-samples`).
- Evaluate raw and adjusted predictions on holdout using `scripts/evaluate_holdout_with_scalers.py`.

Exact metrics — runs and tables

Table 1 — Initial (leakage) per-zone report excerpt

Zone `2227734911` (from `docs/per_zone_report/per_zone_report.json` produced with calibration_pairs_direct.csv):

| zone | n | mae_raw (µg/m³) | rmse_raw (µg/m³) | mae_scaled (µg/m³) |
|------|---:|-----------------:|------------------:|-------------------:|
| 2227734911 | 500 | 14.139943 | 14.139943 | 0.0 |

Notes: this row shows the leakage case where scaling collapsed error to zero because calibration data for this zone contained identical rows.

Table 2 — Holdout evaluation (training-only scalers applied)

Results from `python scripts/evaluate_holdout_with_scalers.py --max-samples 1000 --holdout-hours 336 --scalers data/processed/per_zone_scalers_trained.json` (sample size = 1000).

| metric | raw (normalized) | raw (µg/m³) | scaled (normalized) | scaled (µg/m³) |
|--------|-----------------:|------------:|--------------------:|---------------:|
| MAE    | 0.05899714910509174 | 20.232222726644100 | 0.16488524450233070 | 56.54502025455348 |
| MSE    | 0.00615472117671275 | 723.824911510889000 | 0.10437323570798127 | 12274.796198125272 |
| RMSE   | 0.07845203105537005 | 26.903994341191960 | 0.32306846907115720 | 110.79167928199875 |

Table 3 — Example aggregate comparison observed earlier (calibration-evaluation artifact)

This artifact showed a misleading apparent improvement when scalers were fit on calibration data that overlapped evaluation samples (leakage). Example numbers (from an earlier evaluation run on a limited set, n=214):

| metric | raw MAE (µg/m³) | raw RMSE (µg/m³) | scaled MAE (µg/m³) | scaled RMSE (µg/m³) |
|--------|-----------------:|------------------:|-------------------:|--------------------:|
| value  | 39.02 | 58.64 | 0.93 | 5.51 |

Table 4 — Diagnostics (top rows) from `docs/scaler_diagnostics.csv` (holdout vs training-fit)

| zone | n | raw_mae_ug | scaled_mae_ug | delta_mae | slope (a) | intercept (b) |
|------|---:|-----------:|--------------:|----------:|----------:|--------------:|
| 10079370129 | 14 | 42.424191 | 347.832397 | 305.408206 | 6.026736372995685 | 0.3034469278969944 |
| 10044505589 | 14 | 19.271400 | 248.257779 | 228.986379 | 3.654834476588881 | 0.11141857625330862 |
| 308466202 | 15 | 48.501057 | 264.105670 | 215.604613 | 4.168494746216197 | 0.20988433594829517 |
| 10113391770 | 14 | 9.208124 | 99.751499 | 90.543374 | 3.654834476588881 | 0.11141857625330862 |
| 3130783230 | 14 | 22.647141 | 53.664280 | 31.017139 | 1.4134026821864676 | 0.08753247825233057 |
| 12543439896 | 14 | 35.365199 | 46.001649 | 10.636450 | 0.8741373903155879 | 0.01590668368248575 |
| 6536473096 | 14 | 3.969867 | 14.475000 | 10.505133 | -1.4971818611928715e-16 | 24.04 |
| 2227734911 | 15 | 2.827757 | 6.370774 | 3.543017 | 0.5027758374235655 | 0.017657814907689768 |
| 308874220 | 15 | 2.054811 | 4.740000 | 2.685189 | 1.2953081897705298e-16 | 50.07 |
| 7404868042 | 14 | 2.308757 | 4.391527 | 2.082770 | 1.060552349379105 | 0.023643758501420076 |

Repro commands (summary)

- Generate calibration pairs: `python scripts/generate_calibration_pairs.py --out data/processed/calibration_pairs.csv --max-samples 5000`
- Generate holdout pairs: `python scripts/generate_holdout_pairs.py --out data/processed/holdout_pairs.csv --max-samples 1000`
- Create training-only CSV: remove holdout rows from calibration_pairs.csv to produce `data/processed/training_pairs.csv` (one-liner used in workspace)
- Fit scalers: `python scripts/fit_scalers.py data/processed/training_pairs.csv > data/processed/per_zone_scalers_trained.json`
- Diagnostics: `python scripts/diagnose_scalers.py --holdout data/processed/holdout_pairs.csv --scalers data/processed/per_zone_scalers_trained.json --out docs/scaler_diagnostics.csv`
- Evaluate holdout: `python scripts/evaluate_holdout_with_scalers.py --max-samples 1000 --holdout-hours 336 --scalers data/processed/per_zone_scalers_trained.json`

Artifacts

- `data/processed/calibration_pairs*.csv`, `data/processed/holdout_pairs.csv`, `data/processed/training_pairs.csv`
- `data/processed/per_zone_scalers_trained.json`
- `docs/scaler_diagnostics.csv`, `docs/scaler_coeff_hist.png`, `docs/scaler_sample_hist.png`
- `docs/per_zone_report/per_zone_report.json`, `docs/stpignn_holdout_with_scalers.json`

