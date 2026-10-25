# Resume

- Branch: `audit/canonical-notebook-20261023`.
- S4 complete and pushed at `006ba94`; `results/loso_summary_v2c.csv` records LOSS versus ordinary kriging. Earlier outputs remain unchanged.
- W1 complete: `scripts/input_fix_v2g.py`, `results/input_fix_v2g.json`, `results/input_channels_v2g.csv`, `results/data_v2g_arrays.npz`. Train-only AR-with-lag test MAE/R² 11.894099/0.374211 versus persistence 8.116094/0.532089. PM2.5 and PM10 inputs were capped at 500; PM2.5 lag and target share train-fitted log1p scaling.
- STOP: W1 explicitly requires stopping if AR-with-lag does not approach persistence. It is 46.5% worse on MAE. Report a possible alignment bug; this is not proof of a timestamp shift. W2–W8 are NOT RUN. No routing, IG, or Gate M.
- `results/codex_log/ACTIONS.md`, `DECISIONS.md`, `QUOTA.md`, and `runs/w1_input_fix_v2g.log` were appended; this file alone was overwritten.
- Next action only if the user directs a new investigation: audit raw lag/target pairing and imputation before model training. Preserve S4 and W1 outputs and use new suffixes for any later results.
