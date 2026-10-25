# Resume

- Branch `audit/canonical-notebook-20261023`; latest pushed result before h=3 is `e0fd782`. W1 PASSED and S4 LOSO LOSS remain unchanged. W2 h=1,3,6,24 complete; h=12 queued. W5 partial criteria in `results/benchmark_v2g.md`.
- W6 `python -u -m scripts.evaluate_loso_v2g` is running in exec session 97278, log `results/codex_log/runs/w6_loso_v2g.log`; at 12:52 UTC it reached fold 12/15. It checkpoints ignored `results/loso_predictions_v2g.parquet` after each seed. Once complete inspect summary/decision/unscored files and commit/push. Do not change S4 outputs.
- Five-hour window began 2026-10-25 08:27 UTC, ends near 13:27 UTC. At 12:52 UTC about 35 minutes remain. Commit and push h=3 checkpoint now, then run h=12 while W6 continues. Stop cleanly before the limit and update this file.
- If time allows after W6 and h=12, run W3 DEM, W4 low-data, W7 lambda, W8 citywide in that order. Scripts/configs are predeclared in earlier commits. W4 ten-station cases are coverage BLOCKED, fixed before scores. Append ACTIONS/DECISIONS/QUOTA and runs; overwrite only this RESUME. Earlier outputs unchanged, new outputs `_v2g`.
