# Resume

- Last completed gate: C LOSO. Source commit `e90fd05`, result commit `a08e1e8`; final per-seed and handoff commit follows.
- Current gate: none. Gate C is DONE; no more Gate B/C work is pending.
- Next gate: D h=6 and h=24 cleaned gate (NOT RUN; outside the current user request).
- Branch: `audit/canonical-notebook-20261023`.
- Commit: `a08e1e8` is the Gate C result commit; run `git rev-parse HEAD` for the final handoff commit.
- Running job: none (PID: none; log path: `results/codex_log/runs/gate_c_loso.log` is complete).
- Exact command to continue: `cd /home/jupyter-1nt23cb058/Capstone && cat results/codex_log/RESUME.md && git status --short && cat results/loso_decision_v2.json`.

## Gate A state and evidence

- Cleaned arrays: `results/data_v2_arrays.npz`; fit: `results/data_v2_fit.json`; split: `results/splits_v2.json`; config: `configs/data_v2.yaml`.
- Train PM2.5 observed mean/SD/max: 34.135868/22.993734/493.0 µg/m³. Raw train PM2.5 rows rejected above 500: 887. Horizon-1 scored observed pairs: train 32,628; validation 7,203; test 14,583.
- Old saved `y_clean` versus v2 observed truth disagreements: 41,290 on 55,034 overlapping raw station-hours. The old `y_clean` writer is absent from permitted source files; exact old-cleaner parity is blocked. See `results/old_filtering_audit.md` and `results/cleaning_compare_v2.json`.
- `results/cleaning_counts_v2.csv` is correct: `source` values `station`, `weather`; station train PM2.5 above-cap rows 887. Ten tests passed (`results/codex_log/runs/gate_a_tests.log`).
- Step 4b-A was appended to `claude_paper.md`; do not reread it in full.

## Gate B result (DONE)

- Cleaned h=1 test pairs: 14,583. Persistence MAE/R² 8.116095/0.532089; IDW 22.698642/-0.205856. Validation-selected corrected ST-PIGNN short seed 23 MAE/R² 20.613632/0.001594. Matched-budget primary gate fails against persistence; paired bootstrap details in `results/gate_v2b.md`.
- Five-seed neural and longer rows, raw predictions and curves are in `results/gate_v2b.csv`, `results/neural_final_v2b.csv`, `results/neural_longer_v2b.csv`, and `results/neural_curves_v2b.csv`. Earlier Step 4 outputs were preserved.

## Gate B protocol (DONE)

- The fixed short budget and separate longer diagnostics used `configs/gate_v2b.yaml`, `scripts/train_gate_v2.py`, and `scripts/evaluate_baselines_v2.py`; selection used validation only. The paired UTC-day bootstrap used 2,000 replicates. The predeclared primary gate and Ridge information-set correction are recorded in DECISIONS.md.

## Gate C result (DONE)

- Fifteen folds were considered with three fixed seeds, all valid observed windows, and the held-out station excluded from training, imputation and fitted statistics. Methods: ST-PIGNN known-station lagged PM2.5 with hidden station suppressed; ST-PIGNN weather/static only; GRU-only; IDW; gp_rbf; pykrige ordinary kriging with fitted variogram; nearest-known-station persistence; pooled known-station train mean; Ridge weather/static. The information set is recorded per method in the result CSV.
- Predeclared decision rule: WIN iff known-station ST-PIGNN pooled MAE is below the best IDW/GP/kriging, paired bootstrap CI excludes zero and R² is higher; TIE iff CI includes zero; LOSS otherwise. Result TIE is in DECISIONS.md.
- Fold-isolated builder: `src/stpignn/data_v2.py:build(excluded_station_id=...)`; runner `scripts/evaluate_loso_v2.py`; config `configs/loso_v2.yaml`. Three seeds were chosen before scores due to quota. Four stations had zero observed test targets and were recorded as unscored. `pykrige==1.7.3` was installed.
- Gate C run finished at 2026-10-24 18:21:10 UTC, exit 0, source commit `e90fd05`, runtime 3,284.709 seconds on CUDA. Nine methods each scored 14,583 observed held-out pairs in 11 folds; four mapped stations had zero observed test targets. Outputs: `results/loso_summary_v2.csv`, `results/loso_per_station_v2.csv`, `results/loso_seed_summary_v2.csv`, `results/loso_predictions_v2.parquet`, `results/loso_decision_v2.json`, `results/loso_fallbacks_v2.csv`, `results/loso_unscored_folds_v2.csv`, `results/loso_curves_v2.csv`.
- Predeclared verdict: TIE. Known-station ST-PIGNN MAE/R² 22.282968/-0.049766; best spatial baseline ordinary kriging 22.588024/-0.197255. Paired UTC-day bootstrap MAE difference -0.305056 µg/m³, CI [-1.163714, 0.607623] includes zero; Wilcoxon p=0.278320 over 11 scored stations. Kriging used known-station train-mean fallback on 5,163/14,583 pairs. Step 4b-C is appended to `claude_paper.md`.

## Remaining queue (NOT RUN, in order)

1. D: h=6 and h=24 cleaned gate.
2. E: latency, synchronized, 50 warmup + 200 timed.
3. F: PVR and smoothness with matched lambda=0 and `figures/pvr_vs_gradient.pdf`; Q blocked by absent traffic index.
4. G: ablation with full model, lambda sweep, cone angles, SRTM/none/shuffled/northing/coordinates controls.
5. H: worst-station calibration-fault test.
6. I: Integrated Gradients with named v2 channels and `decay_definition.md`.
7. J: routing only after predicted-field range/correlation gate; use training feature builder.
8. K: figures, Makefile, MANIFEST, and claim verdicts C1–C14 in `claude_paper.md` section 6.
