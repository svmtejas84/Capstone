# Resume

- Branch: `audit/canonical-notebook-20261023`. S4 LOSS at `006ba94`; X1–X5 W1 PASS at `9451488`.
- W2 source preparation complete: `configs/benchmark_v2g.yaml`, `src/stpignn/models_v3.py`, `scripts/benchmark_v2g.py`. All 12 neural model forward/backward calls passed on CUDA; full training has NOT started. Source commit/push follows.
- Fixed input rule: append lag_is_imputed, share train-fitted log1p PM2.5 lag/target scaling, train/select on observed-immediate-lag pairs, score all observed test targets. Validation-only LR and checkpoint selection, five seeds, four LRs, 30 epochs/patience 5, horizons 1/3/6/12/24. Priority order 1/6/24, then 3/12. No test-based tuning or post-score horizon/fold removal.
- Time window started 2026-10-25 08:27 UTC, ends near 13:27 UTC. At 09:13 UTC about 4 hours 14 minutes remained.
- Next after source push: run `python -u -m scripts.benchmark_v2g --horizon 1`, append `results/codex_log/runs/w2_h1_v2g.log`, inspect exit, then checkpoint. Do not start W3–W8 until W2 priority horizons and W5/W6 ordering are addressed or time forces clean handoff.
