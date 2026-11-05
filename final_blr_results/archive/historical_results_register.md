# Historical research results retained

This register supplements `experiment_manifest.json` and the SHA-256 `archive_integrity.csv`. It records outcome status, not a scientific endorsement of every file. The manifest inventories 2,141 files and 27 families, plus a catchall of 318 unmatched `results/` files; 303 of those are run-control records, including 237 archived partial CPU v2j files. Every discovered file has a local checksum, but family-level provenance remains incomplete for some historical outputs. Source branch commit when inspected: `128dd0324deeb23310a93cb2aaa98f2032efb648`.

| Finding | Historical status and evidence |
|---|---|
| Legacy benchmark gain and routing | INVALID/UNVERIFIABLE: comparison used an untrained baseline and lacks paired baseline/persistence predictions; route validation failed. Preserve `results/protocol_inflation_v2h.csv`, `results/research_audit_r1/bengaluru_verification.md`, and legacy notebook/checkpoint. |
| Gate B/C and W1 input | Lag scaling/input defects led to residual and `lag_is_imputed` corrections. Old metrics remain historical and weather shifted (`results/gate_v2b.csv`, `results/gate_v2c.csv`, `results/old_vs_raw*`, R1 audit). |
| W2/W5, W6, W7 and W3 pre-v2j | SUPERSEDED as weather-dependent forecasts by corrected v2j; keep their original values, configurations, predictions and logs under original `results/` paths. `results/weather_timestamp_check_v2i.md` documents +5h30m mislabeling. |
| Original physics and W7 | Original physics benefit was null or negative in earlier controls; shifted-weather W7 trends mostly negative. Corrected v2j h=1/24 lambda check is separate; see `results/lambda_check_v2j.csv`. |
| Group-DRO P3 | LOSS against ridge in LOSO: 21.356246 vs 20.593676 MAE, paired CI for difference [+0.209967,+1.324329], 14,583 pairs (`results/research_audit_r1/bengaluru_verification.md`). |
| Conformal P2 | Undercoverage persists; rolling update may use labels unavailable at h>1 origins. No online coverage guarantee (`results/conformal_v2h.csv`, R1 audit). |
| W3 corrected DEM | All-control criterion null at h=1 and h=24 (`results/dem_study_v2j.csv`, `results/weather_fix_comparison_v2j.csv`). |
| W4 density | INCONCLUSIVE: varying target populations and no per-pair saved predictions; 10-station condition blocked (`results/sensor_density_v2h.csv`, R1 audit). |
| W8 citywide | BLOCKED: only 22 node-hour series for 154,902 road nodes and one known weather source coordinate; projected uniform weather if broadcast (`results/citywide_precheck_v2h.md`). |
| v2j corrected benchmark/LOSO | Numerical results and predictions saved; original ST-PIGNN has no fixed-criterion win across all five horizons, and LOSO neural WIN is absent. These are exploratory because the Bengaluru test set was repeatedly exposed (`results/benchmark_v2j.md`, `results/loso_summary_v2j.csv`). |
| London/Copenhagen | Preliminary feasibility only; no city training or fixed eligibility conclusion. |

Six post-hoc methodological deviations remain explicitly disclosed: (1) residual formulation and lag repair after Gate B/C; (2) expanded learning-rate grid; (3) addition of same-hour-yesterday baseline; (4) W6 LOSO anchor modifications; (5) W7 lambda sweep; (6) later Laplacian-separated W7 criterion after interim test intervals. Exact evidence and line references are in `results/research_audit_r1/protocol_readiness.md`. None was retroactively preregistered. Weather correction is a defect fix, with shifted results retained. All historical Bengaluru test use remains exploratory.
