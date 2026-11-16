# V5 controlled validation — startup

Started 2026-11-15 on `research/controlled-validation-v5`, branching from V4 commit `bb0d06fa73c25e8420c32d09e5da5372c1328d99`. Historical V3/V4 results and checkpoints are read-only. The tracked tree was clean at startup; numerous pre-existing untracked research archives, checkpoints and logs are preserved. NVIDIA Tesla V100-PCIE-32GB has 32,488 MiB free (elevated `nvidia-smi` check). Host storage has 95 GiB free. No V5 jobs are active.

Current stage: inspect authoritative saved evidence, then perform saved-prediction audits. **No V5 training or new-model test scoring has started.** Freeze and commit `PROTOCOL_FREEZE.md` before either. Bengaluru test labels are previously exposed; all V5 inferences are exploratory. No manuscript or London work.

Recovery: `cd /home/jupyter-1nt23cb058/Capstone`; `git branch --show-current`; `git status --short`; `cat final_blr_results/controlled_validation_v5/RESUME.md`; `nvidia-smi`; inspect V3/V4 `REPRODUCIBILITY.md` before using their saved predictions. Historical source array: `final_blr_results/controlled_validation_v3/data_manifests/data_v3_causal_arrays.npz` (SHA-256 `bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202`).

## Saved-data audit and protocol freeze

Saved-prediction audit ran successfully: 602 method/horizon/anchor rows, 20 V3 contrasts, six V4 contrasts, 130 seed rows, 31 common-mask diagnostic rows. The V3 source array hash matched. Protocol SHA-256 `64682686b29660ff336ed6893e257950ce25c3e03683f68de088f6a808825266`; training remains NOT STARTED. Next: commit/push protocol, implement and smoke-test graph/lag/fairness runners, then launch bounded V100 work.

## V100 graph run and pretest amendment

Protocol-freeze commit `0ce92700e264da6e2788225bef5f0a4f327035dc` was pushed before training. Source and preflight implementation commit `44a3f09` was pushed. Graph stage launched under `scripts/run_supervised.sh` at `logs/graph/`; elevated process namespace reports PID 117422, while sandbox-only `ps` cannot see it. The process is RUNNING; check with elevated `bash scripts/run_supervised.sh status final_blr_results/controlled_validation_v5/logs/graph`. Preflight PASS; initial failed NaN equality assertion was test-only and repaired. No V5 test prediction scored. `PROTOCOL_AMENDMENT_01.md` adds 10 six-hour lag-matched graph cells before test scoring; the original protocol hash is unchanged. Next: monitor graph completion, launch lag/cross/fairness sequentially, validate all 160 cells, then score exposed test once.

## Pre-lag fallback parity amendment

`PROTOCOL_AMENDMENT_02.md` SHA-256 `be17ce0e511a57dddc48449e0350ed565455de9f7a824368dfa059e001148922`, commit `77d2e66`, was pushed before any L1 fit or V5 test score. It matches the frozen same-hour-yesterday fallback at T−24, instead of using a newer issue-time fallback. A V100 preflight passed daily-lag value parity, strict-prior source, future-target mutation, graph geometry and common train masks. `LAG24_ELIGIBILITY.csv` shows 12,375/14,583 genuine daily-lag readings for h=1,3,6,12 and zero at h=24. Graph stage remains active; then launch lag, cross and fairness stages sequentially.

## Graph stage complete; lag stage active

All 50 G1/G2 graph cells completed with checked `COMPLETE.json` and selected checkpoint hashes, 1,074.044 recorded V100 fit seconds (0.2983 h), best epochs 10–21. `logs/graph/COMPLETE` exists. The first supervisor attempt exited code 2 after all cells because `run_stage.sh` was edited while Bash was still parsing it; attempt 1 reloaded the script, skipped/verified all complete cells and exited 0. Failure history is retained in `logs/graph/attempts.log`; no fit was discarded. Lag stage launched under supervisor PID 132111 at `logs/lag/`. No V5 test prediction has been generated. Check with elevated `bash scripts/run_supervised.sh status final_blr_results/controlled_validation_v5/logs/lag`; do not launch cross until lag COMPLETE.
