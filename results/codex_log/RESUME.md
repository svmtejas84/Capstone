# Resume

- Branch: `audit/canonical-notebook-20261023`. W1 PASSED; S4 LOSS unchanged. Earlier v2/v2c outputs unchanged.
- W2 priority horizons h=1 and h=6 are complete with all 12 neural models × 5 seeds and five references. Source h=1 `d2ce207`/corrected `aa5044c`, h=6 `a2596c8`; h=6 result commit/push follows. `results/benchmark_runs_v2g.csv`, `benchmark_selection_v2g.csv`, per-seed `benchmark_predictions_h*_..._v2g.parquet`, `benchmark_v2g.csv`/`.md`, `horizon_curve_v2g.csv`, `figures/horizon_curve.pdf` are checkpoints.
- h=1 A and B meet the paired UTC-day win rule; C physics support not met. h=6 A/B/C do not beat both persistence and same-hour-yesterday. h=6 persistence/same-hour-yesterday/A/B/C/original ST-PIGNN MAE: 16.606891/14.130312/15.780365/15.127259/16.406056/14.840548 µg/m³. Full R² and CIs in benchmark files.
- Fixed input rule: lag_is_imputed channel; shared train-fitted log1p PM2.5 lag/target space; observed-immediate-lag train and validation selection; all observed test targets scored. No test tuning or score-based horizon/fold removal.
- Five-hour window began 2026-10-25 08:27 UTC, ends near 13:27 UTC; at 09:51 about 3 hours 36 minutes remain.
- Next: after h=6 push, run `python -u -m scripts.benchmark_v2g --horizon 24`, summarize h=1/6/24, commit/push. Then W5/W6, h=3/12, W3, W4, W7, W8 in the user's priority order. W3/W4/W6/W7/W8 have NOT RUN. W4 10-training-station cases are coverage BLOCKED (only eight eligible stations), predeclared before W4 scores.
