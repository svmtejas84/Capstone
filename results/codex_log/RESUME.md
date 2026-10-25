# Resume

- Branch: `audit/canonical-notebook-20261023`. W1 PASSED; S4 LOSS unchanged; earlier v2/v2c outputs unchanged.
- W2 priority horizons h=1, 6 and 24 are complete: 12 neural models × five seeds plus five references at each horizon; source commits `d2ce207`/`aa5044c`, `a2596c8`, `ac40419`. h=24 result commit/push follows. Checkpoint files `results/benchmark_runs_v2g.csv`, `benchmark_selection_v2g.csv`, per-seed `benchmark_predictions_h*_..._v2g.parquet`, `benchmark_v2g.csv`/`.md`, `horizon_curve_v2g.csv`, `figures/horizon_curve.pdf`.
- W5 priority-horizon criterion: A/B meet win rule at h=1; B also meets at h=24. C physics-in-architecture criterion not met. h=24 persistence/same-hour-yesterday/A/B/C/original ST-PIGNN MAE/R² are in `results/horizon_curve_v2g.csv`; B h=24 MAE/R² 13.657661/0.400369 vs 14.130312/0.283173 for both references, paired ΔMAE CI [-0.774896,-0.195378]. No horizon/fold dropped after scores.
- Input rule: lag_is_imputed channel, shared train-fitted log1p PM2.5 lag/target space, observed-immediate-lag train/validation selection, all observed test targets scored. No test tuning.
- Five-hour window began 2026-10-25 08:27 UTC, ends near 13:27 UTC; at 10:07 about 3 hours 20 minutes remain.
- Next: after h=24 push, run `python -u -m scripts.evaluate_loso_v2g` to complete W6, commit/push. Then h=3/12, W3, W4, W7, W8. W3/W4/W6/W7/W8 have NOT RUN. W4 10-training-station cases are coverage BLOCKED (only eight eligible stations), predeclared before W4 scores.
