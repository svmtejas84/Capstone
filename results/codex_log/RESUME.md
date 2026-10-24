# Resume

- Last completed gate: A CLEANING. Gate A result commit `e7dbbcd` was pushed to `origin/audit/canonical-notebook-20261023`.
- Current gate: B CLEANED GATE, h=1; STARTED 2026-10-24 16:07:40 UTC. Gate C LOSO is NOT RUN.
- Next gate: C LOSO, after Gate B is committed and pushed.
- Branch: `audit/canonical-notebook-20261023`.
- Commit: Gate B code commits `4261e2e` and `3688c6e`; use `git rev-parse HEAD` for latest branch commit.
- Running job: Gate B summary/bootstrap PID `2881113`, log `results/codex_log/runs/gate_b_summary.log`. Baselines, validation selection, five-seed short final and five-seed longer diagnostics completed; raw logs `results/codex_log/runs/gate_b_*.log`.
- Exact command to continue: `cd /home/jupyter-1nt23cb058/Capstone && cat results/codex_log/RESUME.md && ps -p 2881113 -o pid=,stat= && cat results/codex_log/runs/gate_b_summary.log && cat results/gate_v2b.md`.

## Gate A state and evidence

- Cleaned arrays: `results/data_v2_arrays.npz`; fit: `results/data_v2_fit.json`; split: `results/splits_v2.json`; config: `configs/data_v2.yaml`.
- Train PM2.5 observed mean/SD/max: 34.135868/22.993734/493.0 µg/m³. Raw train PM2.5 rows rejected above 500: 887. Horizon-1 scored observed pairs: train 32,628; validation 7,203; test 14,583.
- Old saved `y_clean` versus v2 observed truth disagreements: 41,290 on 55,034 overlapping raw station-hours. The old `y_clean` writer is absent from permitted source files; exact old-cleaner parity is blocked. See `results/old_filtering_audit.md` and `results/cleaning_compare_v2.json`.
- `results/cleaning_counts_v2.csv` is correct: `source` values `station`, `weather`; station train PM2.5 above-cap rows 887. Ten tests passed (`results/codex_log/runs/gate_a_tests.log`).
- Step 4b-A was appended to `claude_paper.md`; do not reread it in full.

## Gate B instructions (NOT RUN)

- Append `START Gate B` to ACTIONS.md and start time to QUOTA.md before work. Preserve old Step 4 artifacts; write new `results/gate_v2b.csv`, `results/gate_v2b.md`, curves and run metadata with new names.
- Use cleaned `results/data_v2_arrays.npz` and identical observed masks. Baselines: persistence, hour×day-of-week climatology, IDW and Ridge. Neural: GRU-only, Vanilla GCN, ST GRU-GCN, corrected observed-only ST-PIGNN, Laplacian control; five seeds, validation-only LR grid 3e-6/1e-5/3e-5/1e-4/3e-4, same short budget as Step 4. Add one longer 20-epoch/patience-4 row for corrected ST-PIGNN and GRU-only.
- Paired UTC-day bootstrap, 2,000 replicates, selected ST-PIGNN versus persistence and IDW for MAE and R². Report test results even if unfavorable. Run long jobs with nohup and record PID/log; poll no more than every five minutes. Append short Step 4b-B only. Finish with `git add -A` (no data/ or >90 MB), commit, push, then update this file and push its handoff commit.

## Gate C instructions (NOT RUN)

- Fifteen LOSO folds, five seeds (three only if quota tight, logged), all valid windows, held-out station excluded from training, imputation and fitted statistics. Methods: ST-PIGNN known-station lagged PM2.5 with hidden station suppressed; ST-PIGNN weather/static only; GRU-only; IDW; gp_rbf; pykrige ordinary kriging with fitted variogram; nearest-known-station persistence; station train mean; Ridge weather/static. Record information set per row. Output `results/loso_per_station_v2.csv`, `results/loso_summary_v2.csv`, pooled/per-station MAE/RMSE/R², paired bootstrap CIs and Wilcoxon over stations.
- Predeclared decision: WIN iff ST-PIGNN known-stations pooled MAE is below the best IDW/GP/kriging, paired bootstrap CI excludes zero and R² is higher; TIE iff CI includes zero; LOSS otherwise. Write result to DECISIONS.md without changing rule after scores. Append Step 4b-C, commit/push, update this file.

## Remaining queue (NOT RUN, in order)

1. D: h=6 and h=24 cleaned gate.
2. E: latency, synchronized, 50 warmup + 200 timed.
3. F: PVR and smoothness with matched lambda=0 and `figures/pvr_vs_gradient.pdf`; Q blocked by absent traffic index.
4. G: ablation with full model, lambda sweep, cone angles, SRTM/none/shuffled/northing/coordinates controls.
5. H: worst-station calibration-fault test.
6. I: Integrated Gradients with named v2 channels and `decay_definition.md`.
7. J: routing only after predicted-field range/correlation gate; use training feature builder.
8. K: figures, Makefile, MANIFEST, and claim verdicts C1–C14 in `claude_paper.md` section 6.
