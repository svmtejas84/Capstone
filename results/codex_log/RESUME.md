# Resume

- Branch: `audit/canonical-notebook-20261023`. W1 PASSED; S4 LOSS unchanged. Earlier outputs unchanged.
- W2 h=1 is complete: fixed 4-LR validation search, all 12 neural methods × 5 seeds, five references, 14,583 observed test pairs. Source commits `d2ce207` and corrected reference/report source `aa5044c`; result commit/push follows. Raw `results/benchmark_runs_v2g.csv`, `benchmark_selection_v2g.csv`, `benchmark_predictions_h1_*_v2g.parquet`; summaries `results/benchmark_v2g.csv`/`.md`, `horizon_curve_v2g.csv`, `figures/horizon_curve.pdf`.
- h=1 A MAE/R² 8.056366/0.547921 and B 8.025968/0.543357 meet the paired-day win rule versus both persistence 8.116095/0.532089 and same-hour-yesterday 14.130312/0.283173. C 9.320887/0.546394 does not meet the physics-support criterion. Original penalty ST-PIGNN 8.018825/0.585597. Full per-model metrics and CI in benchmark files.
- Input rule for all neural models/references: lag_is_imputed channel, shared train-fitted log1p PM2.5 lag/target transform, observed-immediate-lag training/selection, all observed test target scoring. No test-based tuning.
- Time window began 2026-10-25 08:27 UTC; stop near 13:27 UTC if needed. At 09:30 UTC about 3 hours 57 minutes remained.
- Next: run `python -u -m scripts.benchmark_v2g --horizon 6`, then h=24, commit/push each complete horizon; then W5, W6, remaining h=3/12, W3, W4, W7, W8 in the requested priority order. Prepared scripts for W3–W8 are at source commit `aa5044c` but those experiments have NOT RUN.
