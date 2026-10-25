# Resume

- Last completed step: S3 physics controls. S1, S2 and S3 are complete; S3 result commit follows. Original Gate B/C results remain unchanged.
- Branch: `audit/canonical-notebook-20261023`.
- Latest commit: HEAD after S3 result commit; run `git rev-parse HEAD` to resolve its hash. S3 source commit `107388b`.
- Running job: none (PID: none; `results/codex_log/runs/s3_physics_controls.log` complete).
- NEXT: S4 LOSO residual rerun. S1 found a defect, so S4 is required by the user's rule. After S4, append factual Step 4c tables/source lines to `claude_paper.md`, commit/push, and STOP before D-M.
- Exact continue command: `cd /home/jupyter-1nt23cb058/Capstone && cat results/codex_log/RESUME.md && git rev-parse HEAD && git status --short`.

## Completed evidence

- S1: `results/diagnosis_v2c.md`, source commit `38f477f`. Training lag-target r=0.040120, immediately observed lag r=0.823055; three training lag values exceed 500 µg/m³, max 44,428.418. Input and target transforms differed; no timestamp shift identified. Train-only AR test MAE 20.562207 versus persistence 8.116095.
- S2: `results/gate_v2c.csv`, `.md`, `gate_v2c_bootstrap.json`, source summary commit `012ace7`, config `configs/gate_v2c.yaml`, seeds [11,23,37,51,79]. Validation-selected corrected ST-PIGNN seed11 test MAE/R² 8.401826/0.589756 versus persistence 8.116095/0.532089. Paired MAE difference +0.285730 µg/m³, 95% UTC-day CI [+0.183806,+0.393342]; primary gate NO. Corrected five-seed mean MAE 8.259108±0.185399. Alternate train-tail selection reported separately, seed11 test MAE/R² 8.127372/0.578965.
- S3: `results/physics_controls_v2c.csv`, `.md`, `.json`, script `scripts/physics_controls_v2c.py`, config `configs/gate_v2c.yaml`, seeds [11,23,37,51,79], source commit `107388b`, run 2026-10-25T04:09:31 UTC. Corrected MAE/PVR(0) 8.259108/46.031300%; matched lambda=0 8.160498/45.924339%; Laplacian 8.282859/46.122834%. Paired 95% seed-t intervals include zero, so predeclared verdict NO change beyond seed noise. Q absent (no measured traffic index).

## S4 NOT RUN instructions

- Prepared runner: `scripts/evaluate_loso_v2c.py` (must be committed before execution). Same Gate C 15-fold/11-scorable-station protocol, seeds [11,23,37], fixed LOSO config `configs/loso_v2.yaml`, fold-isolated `data_v2.build`, same WIN/TIE/LOSS rule. Hidden station own PM2.5 excluded from training and fits. Residual ST-PIGNN known-stations variant uses causal nearest-known-station persistence as the hidden residual anchor; weather/static and GRU-only variants use known-station train-mean anchor. Baselines include nearest-known-station persistence. Predeclare this in DECISIONS.md before running. Output `results/loso_summary_v2c.csv` and companion per-station/prediction/decision files. Four original Gate C folds have zero observed test targets.
- Append factual Step 4c to `claude_paper.md` with S1-S4 tables and source lines; do not reread the full file. Stop after S4.

## Original results and NOT RUN queue

- Original Gate B: `results/gate_v2b.csv`/`.md`; persistence MAE/R² 8.116095/0.532089, corrected ST-PIGNN 20.613632/0.001594.
- Original Gate C: TIE; `results/loso_summary_v2.csv`, `results/loso_decision_v2.json`; 11 scored folds, 14,583 observed test pairs.
- After S4, NOT RUN: D cleaned h=6/24; E latency; F PVR/smoothness; G ablation; H calibration; I IG; J routing; K figures/claim verdicts; L citywide conditional; M London conditional.
