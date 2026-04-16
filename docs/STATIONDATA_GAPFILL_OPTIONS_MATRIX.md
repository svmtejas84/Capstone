# Gapfill Options Matrix

This matrix is model-agnostic and can support GNN, GRU, GCN, or pure inference workflows.
Raw files under `data/raw/` must remain immutable.

## Principles

- Keep observed values unchanged.
- Write imputed values to a separate derived layer.
- Track provenance and uncertainty for every imputed point.
- Gate methods using backtesting before production use.

## Candidate Methods

| Method | Best For | Strengths | Risks | Production Use |
|---|---|---|---|---|
| Temporal linear interpolation | Short in-station gaps | Simple, high coverage, low complexity | Fails for long outages or abrupt regime shifts | Default for short gaps |
| Temporal climatology (hour x weekday) | Seasonal/diurnal behavior | Stable fallback, robust to noise | Can smooth out real events | Fallback when linear fails |
| Spatial IDW | Dense neighboring stations at same timestamp | Uses network spatial signal | Weak in sparse station-time slices | Secondary signal, not sole method |
| Hybrid temporal + IDW | Mixed temporal/spatial availability | Usually more robust than single-source | Weight tuning needed | Strong candidate for medium gaps |
| Station median baseline | Sparse metadata-only fallback | Always available | Low fidelity | Last-resort fallback |
| Physics-informed correction | Wind/plume-constrained estimates | Most scientifically defensible | Higher engineering/validation burden | High-value zones and stress periods |
| State-space / Kalman | Smooth temporal dynamics | Handles sensor noise and drift | Parameter sensitivity | Optional advanced temporal model |
| Probabilistic/Bayesian fusion | Uncertainty-aware decisions | Calibrated confidence intervals | Highest complexity | Policy and risk-sensitive decisions |

## Recommended Rollout

1. Tier A (observed): direct measurements only.
2. Tier B (high-confidence imputed): temporal linear and hybrid where backtests pass gates.
3. Tier C (low-confidence inferred): long-gap fallback and sparse-region estimates.
4. Train/evaluate with Tier A + Tier B targets; reserve Tier C for features or scenario analysis.

## Required Metadata For Every Filled Row

- `is_imputed`
- `impute_method`
- `impute_confidence`
- `impute_uncertainty`
- `impute_source_count`
- `impute_run_id`

## Validation Gates (Minimum)

- Backtest patterns: random points, contiguous outage blocks, station-level outages.
- Metrics by pollutant and year: MAE, RMSE, sMAPE.
- Acceptance rule: method is production-eligible only if it beats station-median baseline and maintains high coverage.

## Current Workspace Artifacts

- Method benchmark scores: `data/processed/gapfill/gapfill_benchmark_method_scores.parquet`
- Method policy snapshot: `data/processed/gapfill/gapfill_selected_method_policy.parquet`
- Method benchmark report: `data/processed/gapfill/gapfill_benchmark_report.md`
- Derived station layer: `data/processed/gapfill/station_timeseries_observed_imputed.parquet`
- Derived missing index: `data/processed/gapfill/station_timeseries_unresolved_index.parquet`
- Derived method summary: `data/processed/gapfill/station_timeseries_imputation_summary.parquet`
- Derived build report: `data/processed/gapfill/station_timeseries_imputation_build_report.md`
- Evaluator script: `scripts/evaluate_gapfill_options.py`
- Derived builder script: `scripts/build_gapfill_derived_layer.py`

## Executed Pipeline

1. `python scripts/evaluate_gapfill_options.py --sample-per-pollutant 400`
2. `python scripts/build_gapfill_derived_layer.py`

## Observed Outcome Snapshot

- Evaluator selected `temporal_linear` as primary method across pollutants in the current benchmark sample.
- Derived build produced 1,073,807 materialized rows with 777,350 imputed rows.
- Tier distribution in derived output:
	- Tier A (observed): 296,457
	- Tier B (higher-confidence imputed): 51,614
	- Tier C (lower-confidence inferred): 725,736

## Notes For Downstream Models

- Raw station files remain unchanged.
- Use `is_imputed`, `impute_tier`, and `impute_method` as training/inference controls.
- For strict supervision, prioritize Tier A and Tier B labels.
