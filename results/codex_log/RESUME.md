# Resume

- Last completed step: S1 diagnosis. Source commit `38f477f`; final S1 result commit follows. S1 identified an imputed-lag and scaling defect. Original Gates B/C remain unchanged and final.
- Branch: `audit/canonical-notebook-20261023`.
- Latest commit: HEAD after the S1 result commit; use `git rev-parse HEAD` to resolve its hash. Pre-result source commit `38f477f`.
- Running job: none (PID: none; log path: `results/codex_log/runs/s1_diagnose.log` is complete).
- NEXT: S2 residual formulation, then S3 physics controls, then S4 LOSO rerun. S4 is required under the user's rule because S1 found a defect. The full S1-S4 instructions are in the latest user message of this session.
- Exact continue command: `cd /home/jupyter-1nt23cb058/Capstone && cat results/codex_log/RESUME.md && git rev-parse HEAD && git status --short`.

## Completed S1 evidence

- Script `scripts/diagnose_v2c.py`, configs `configs/data_v2.yaml` and `configs/gate_v2b.yaml`, seed 42, checkpoint seeds 11/23/37/51/79, source commit `38f477f`, final run 2026-10-25T02:43:01 UTC. Raw report `results/diagnosis_v2c.md`, JSON and CSV companions.
- Training lag-target r=0.040120 over 32,628 observed target pairs; immediately observed lag r=0.823055 over 30,974 pairs. Three training lag values exceed 500 µg/m³ and the maximum is 44,428.418 µg/m³. Feature SD=562.017 µg/m³. Neural targets use a separate log1p transform. Train-only AR test MAE/R² 20.562207/-0.073372; Ridge lag+weather/static 20.485240/0.059078; persistence 8.116095/0.532089.
- Four LOSO stations 5547, 5548, 6975, 2498781 have zero observed test targets. No timestamp shift was identified. S1 defect is input imputation/scaling, not proof of a target-time alignment bug.

## S2-S4 instructions (NOT RUN)

- S2: residual prediction for ALL five neural models (GRU-only, Vanilla GCN, ST GRU-GCN, ST-PIGNN corrected, ST-PIGNN Laplacian), LR grid 3e-6/1e-5/3e-5/1e-4/3e-4/1e-3/3e-3, max 20 epochs, patience 4, 5 seeds. Select on validation and separately report selection on the last 30 train days. Paired UTC-day bootstrap 2,000 for ST-PIGNN versus persistence and best classical baseline. New outputs only with `_v2c` suffix. Predeclare choices in DECISIONS.md before run.
- S3: corrected versus matched lambda=0 versus Laplacian, same seeds/budget; PVR thresholds 0/0.01/0.05/0.1 normalized and µg/m³, edge gradient, Dirichlet energy. Output `results/physics_controls_v2c.csv`.
- S4: rerun LOSO with S2 formulation, same Gate C protocol and WIN/TIE/LOSS rule, plus nearest-known-station persistence; note four unscored folds. Output `results/loso_summary_v2c.csv`. Triggered by S1 defect. Append factual Step 4c tables/source lines to `claude_paper.md` after S4; stop before D-M.

## Existing results and NOT RUN queue

- Gate B: `results/gate_v2b.csv`/`.md`; persistence MAE/R² 8.116095/0.532089, IDW 22.698642/-0.205856, corrected ST-PIGNN 20.613632/0.001594.
- Gate C: TIE; `results/loso_summary_v2.csv` and `results/loso_decision_v2.json`; 11 scored folds and 14,583 observed test pairs.
- After S4, NOT RUN: D cleaned h=6/24; E latency; F PVR/smoothness; G ablation; H calibration; I IG; J routing; K figures/claim verdicts; L citywide conditional; M London conditional.
