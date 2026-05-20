**Summary**

This document records the scaler evaluation work performed for ST-PIGNN post-prediction calibration. It lists the initial target scaling, the offline evaluation procedure used to detect leakage and overfitting, the artifacts produced, and recommended safe thresholds and next steps before any runtime deployment.

**Key Constants**

- **TARGET_SCALE**: 342.9356 (used in scripts/generate_calibration_pairs.py and inference code)
- **TARGET_PM25_MAX**: 120.0 (clipping applied when converting to µg/m³)

**High-level workflow executed**

1. Regenerate paired model predictions and observations in µg/m³ using the model and processed inputs (scripts/generate_calibration_pairs.py).
2. Create a holdout sample set (scripts/generate_holdout_pairs.py) and remove those rows from calibration data to produce a training-only CSV (data/processed/training_pairs.csv).
3. Fit per-zone linear scalers (least-squares) on the training pairs: scripts/fit_scalers.py data/processed/training_pairs.csv -> data/processed/per_zone_scalers_trained.json.
4. Evaluate on holdout using scripts/evaluate_holdout_with_scalers.py to compare raw vs adjusted predictions on unseen timestamps.
5. Produce per-zone diagnostics and visualizations (scripts/per_zone_report.py, scripts/diagnose_scalers.py) to inspect sample counts, slope distributions, and per-zone MAE deltas.

**Artifacts produced**

- Calibration CSVs:
  - data/processed/calibration_pairs.csv
  - data/processed/calibration_pairs_direct.csv
  - data/processed/holdout_pairs.csv
  - data/processed/training_pairs.csv
- Scalers:
  - data/processed/per_zone_scalers.json (initial)
  - data/processed/per_zone_scalers_trained.json (trained on training-only)
- Diagnostics & reports:
  - docs/per_zone_report/per_zone_report.json
  - docs/scaler_diagnostics.csv
  - docs/scaler_coeff_hist.png
  - docs/scaler_sample_hist.png
  - docs/stpignn_holdout_with_scalers.json

**Commands to reproduce (recommended order)**

1) Generate calibration pairs: python scripts/generate_calibration_pairs.py --out data/processed/calibration_pairs.csv --max-samples 5000
2) Generate holdout pairs: python scripts/generate_holdout_pairs.py --out data/processed/holdout_pairs.csv --max-samples 1000
3) Create training-only CSV by removing holdout rows from calibration_pairs.csv. Example python one-liner used in workspace to produce data/processed/training_pairs.csv.
4) Fit scalers: python scripts/fit_scalers.py data/processed/training_pairs.csv > data/processed/per_zone_scalers_trained.json
5) Produce diagnostics: python scripts/diagnose_scalers.py --holdout data/processed/holdout_pairs.csv --scalers data/processed/per_zone_scalers_trained.json --out docs/scaler_diagnostics.csv
6) Run holdout evaluation: python scripts/evaluate_holdout_with_scalers.py --max-samples 1000 --holdout-hours 336 --scalers data/processed/per_zone_scalers_trained.json
7) Produce per-zone report: python scripts/per_zone_report.py

**Observed outcomes (summary)**

- Initial evaluation using calibration data showed a leakage case: a single zone (2227734911) with identical rows produced a fitted scaler that collapsed scaled error to zero — a sign of data-leakage / single-zone dominance.
- After regenerating calibration/holdout splits and fitting on training-only samples, holdout evaluation produced realistic raw metrics (e.g., raw MAE ≈ 20.23 ug/m^3) while naïve per-zone scaling often increased error (scaled MAE larger), indicating overfitting or inversion issues in many per-zone fits.

**Likely failure modes identified**

1) Overfitting per-zone when sample counts are small.
2) Distribution shift between calibration and holdout timestamps (sensor drift, seasonal effects).
3) Transform direction mistakes (fitting reference->sensor but applying sensor->reference).
4) A few unstable zones dominating aggregated metrics.
5) Unbounded or pathological slope/intercept values from small or degenerate samples.

**Recommended safety checks before storing scalers to Redis / enabling runtime correction**

- Minimum samples per-zone: MIN_SAMPLES = 30 (do not accept scalers trained on fewer samples).
- Maximum absolute slope: MAX_ABS_SLOPE = 3.0 (clip or reject fits with |a| > 3).
- Minimum explained variance: compute R^2 and require MIN_R2 = 0.2.
- Reject fits with intercepts that push predictions outside physical bounds (negative or >120 ug/m^3 after adjustment).
- If a per-zone fit is rejected, fallback order: global scaler -> regional aggregator -> raw prediction.

**Suggested implementation to safely store scalers**

1) Extend scripts/fit_scalers.py to compute R^2 and include r2 and n in output JSON.
2) Add a scripts/store_scalers_redis.py --safe mode that only writes scalers passing thresholds and records version, min_samples, and rejected=true|reason metadata.
3) Keep runtime code (router/prediction_scaler.py and router/api/routes.py) behind a feature flag and audit every decision (store scaler version in stake_audit.create_audit(meta=...)).

**Next steps / recommendations**

- Do not write to Redis or enable runtime scaling until the safe-store is implemented and a pass/fail check on held-out metrics is done.
- Consider regularized fits (Ridge) or pooling (Bayesian hierarchical linear model) to stabilize per-zone coefficients.
- Add automated unit/regression tests that validate transform direction and holdout performance.
- If deploying, use a shadow/canary rollout and monitor live performance closely before making decisions based on adjusted predictions.

**Contact / notes**

This file was generated as part of the evaluation run; see the scripts in the `scripts/` directory for reproducible steps. If you want, I can implement the safe-store and automatic thresholds next and re-run the holdout evaluation to produce a final list of scalers approved for deployment.
