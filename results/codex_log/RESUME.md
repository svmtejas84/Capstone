# Resume

- Last completed step: S2 residual gate. S1 diagnosis and S2 are complete; source commits `38f477f` (S1) and `012ace7` (final S2 summary source). S2 result commit follows. Original Gate B/C results remain unchanged.
- Branch: `audit/canonical-notebook-20261023`.
- Latest commit: HEAD after the S2 result commit; run `git rev-parse HEAD` to resolve its hash. Current pre-result commit `012ace7`.
- Running job: none (PID: none; S2 logs under `results/codex_log/runs/s2_*.log` are complete).
- NEXT: S3 physics controls, then S4 LOSO rerun. S4 is required by the user's rule because S1 found an imputed-lag/scaling defect. After S4 append factual Step 4c to `claude_paper.md` and STOP; do not start D-M.
- Exact continue command: `cd /home/jupyter-1nt23cb058/Capstone && cat results/codex_log/RESUME.md && git rev-parse HEAD && git status --short`.

## Completed evidence

- S1: `results/diagnosis_v2c.md`, script `scripts/diagnose_v2c.py`, configs `configs/data_v2.yaml`/`gate_v2b.yaml`, source commit `38f477f`. Training lag-target r=0.040120, immediate observed-lag r=0.823055; three training lag values exceed 500 µg/m³, max 44,428.418. Input lag and target transforms differ. Train-only AR test MAE 20.562207 versus persistence 8.116095. No timestamp shift identified.
- S2: `results/gate_v2c.csv`, `results/gate_v2c.md`, `results/gate_v2c_bootstrap.json`, configs `configs/gate_v2c.yaml`/`data_v2c_tail.yaml`, scripts `scripts/train_gate_v2.py`/`summarize_gate_v2c.py`, seeds [11,23,37,51,79]. All five neural models received the same causal last-observed anchor and residual formulation. LR grid [3e-6,1e-5,3e-5,1e-4,3e-4,1e-3,3e-3], max20/patience4. Validation-selected corrected ST-PIGNN seed11 test MAE/R² 8.401826/0.589756 versus persistence 8.116095/0.532089; paired MAE difference +0.285730, 95% UTC-day CI [+0.183806,+0.393342]. Five-seed corrected mean MAE 8.259108±0.185399. Train-tail-selected seed11 test MAE/R² 8.127372/0.578965. It was not substituted into the primary validation-selected gate.
- Classical comparator selected by validation MAE only: climatology. Original Gate B/C outputs are unchanged; all revised outputs use `_v2c`.

## S3/S4 NOT RUN instructions

- S3: matched corrected versus lambda=0 versus Laplacian, same five seeds and 20-epoch/patience-4 budget, corrected-selected LR for lambda=0. PVR normalized thresholds 0/0.01/0.05/0.1 (also in µg/m³ using cleaned train target SD), mean absolute edge gradient and Dirichlet energy. Runner prepared at `scripts/physics_controls_v2c.py`; predeclare the seed-noise verdict rule in DECISIONS before running. Output `results/physics_controls_v2c.csv` and a factual verdict.
- S4: same Gate C 15-fold/11-scorable-station protocol and WIN/TIE/LOSS rule using S2 residual formulation; include nearest-known-station persistence, note four unscored folds. S1 defect triggered rerun. Output `results/loso_summary_v2c.csv`; if impossible, log blocker. Append factual Step 4c tables/source lines to `claude_paper.md` after S4.

## Existing results and NOT RUN queue

- Original Gate B: `results/gate_v2b.csv`/`.md`; persistence MAE/R² 8.116095/0.532089, corrected ST-PIGNN 20.613632/0.001594.
- Original Gate C: TIE; `results/loso_summary_v2.csv` and `results/loso_decision_v2.json`; 11 scored folds and 14,583 observed test pairs.
- After S4, NOT RUN: D cleaned h=6/24; E latency; F PVR/smoothness; G ablation; H calibration; I IG; J routing; K figures/claim verdicts; L citywide conditional; M London conditional.
