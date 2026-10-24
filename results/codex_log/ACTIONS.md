# Gate actions

- 2026-10-24 15:17:38 UTC START Gate A: audit old PM2.5 filtering and rebuild cleaned data. Branch `audit/canonical-notebook-20261023`, starting commit `7d8e7d27a46d554da5284edea68f227d8d246383`.
- Gate A audit job attempt PID 2874060 ended without outputs or a log; reran under a persistent nohup session with PID 2874545 and log `results/codex_log/runs/gate_a_audit.log`.
- 2026-10-24 15:55 UTC DONE Gate A analysis: old-v2 comparison completed; 887 raw train PM2.5 rows above 500 rejected; h=1 scored pairs 32,628/7,203/14,583; train observed max 493.0 µg/m³; 10 tests passed. Source commit `7484720`, config `configs/data_v2.yaml`, seed 42; raw logs in `runs/gate_a_*`.
- 2026-10-24 15:58 UTC DONE Gate A: result commit `e7dbbcd` pushed to `origin/audit/canonical-notebook-20261023`; RESUME.md updated for Gate B. No Gate B job was started.
- 2026-10-24 16:07:40 UTC START Gate B: cleaned h=1 baselines and five-seed neural comparison. Starting commit `7233414cad3a47662a1c03b19bf2d66d42da4932`.
- 2026-10-24 16:49 UTC DONE Gate B analysis: cleaned h=1 five-seed short and longer diagnostics, baselines, paired UTC-day bootstrap. Primary gate fails against persistence; raw outputs in `results/gate_v2b.*` and `runs/gate_b_*.log`. Neural source commit `4261e2e`, baseline/summary source commit `3688c6e`.
- 2026-10-24 16:51 UTC DONE Gate B: result commit `46924c5` pushed to `origin/audit/canonical-notebook-20261023`; RESUME.md set to Gate C with no running job.
- 2026-10-24 17:01:44 UTC START Gate C: cleaned 15-fold leave-one-station-out comparison. Starting commit `ebb0d13`; predeclared WIN/TIE/LOSS rule remains fixed in RESUME.md.
