# Controlled validation v3 — verification record

Verification date: 2026-11-15 UTC. Branch: `research/controlled-validation-v3`. The September 2025–March 2026 test period is exposed, so these checks verify computation and provenance, not independent scientific confirmation.

## Data and fitting gates

1. `PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/test_full_future_mutation.py` passed on the repaired pollutant-hour array; its saved record is `full_future_mutation.json`. The initial candidate array failed; the 74 attempted fits on it remain in `training/invalidated_pre_causal_shift/` and are excluded from all test metrics.
2. `PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/smoke_gpu.py` passed 512×12×15×18 forward/backward, finite gradients and a 1.21 GB allocated peak (`smoke_gpu.json`). Baseline one-batch smokes passed earlier and are logged in v3 `RESUME.md`.
3. `PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/verify_training.py` passed all 20 corrected LR-selection and 125 matched final regularizer cells, including the repaired-array and checkpoint hashes.
4. `PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/verify_baselines.py final` passed all 120 baseline LR-selection and 150 final baseline cells, including model identity, checkpoint/array hashes, epochs and validation-chosen LR. A validation-only checkpoint-reload smoke reproduced h6 seed-11 MAEs on 6,656 matched observed targets.
5. The controlled final training and both one-time test scorers ran through `scripts/run_supervised.sh`; every final stage exited 0 on attempt 0 and has a `COMPLETE` marker. No test scorer was restarted.

## Saved-output and statistical checks

`PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/verify_results.py` returned `status: PASS` and wrote `results_verification.json`:

- Seven source artifact hashes and sizes matched the frozen `data_manifests/source_checksums.csv`.
- All 355 saved control/baseline MAE, RMSE, R² and counts recomputed from per-pair NPZ predictions within the declared numerical tolerance (absolute 1e−5, relative 1e−7).
- All controls and baselines used the same 14,583 target timestamp/station/truth triples at every horizon.
- All 20 frozen true-wind-versus-control mean paired differences, 2,000-draw seven-day moving-block intervals, 100,000-draw block sign-flip p-values and the 20-member Holm adjustment reproduced. The sign-flip and bootstrap RNG streams are independent as frozen in `STATISTICAL_PLAN_ADDENDUM.md`.
- `scripts/secondary_diagnostics.py` saved 1,200 temporal per-station rows and 20 seed sign tests; these do not constitute spatial holdout validation.
- `scripts/wind_cone_diagnostics.py` saved 100 descriptive threshold/variant/horizon rows. It evaluates only arcs with observed targets at both endpoints and cannot establish atmospheric mass conservation.

## Tables, figures and code

`PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/build_results.py` completed after a presentation-only fix for the host's outdated Jinja2 dependency. It wrote eight CSV/LaTeX tables and six figures in PNG/PDF/SVG. A separate check opened all six PNGs with Pillow, checked PDF headers, parsed all six SVGs, and confirmed one CSV/LaTeX pair for each T1–T8. The table row counts are 1, 80, 150, 125, 125, 20, 1, 5. T7's sole row explicitly says **NOT EVALUATED** for a new spatial holdout. All six figures were visually inspected; the effective-λ figure now shows the actual five-epoch schedule and checkpoint epoch distribution, with no misleading zero-variance y-axis zoom.

`python -m py_compile final_blr_results/controlled_validation_v3/scripts/*.py`, `bash -n` on the v3 shell runners, and `git diff --check` passed. `data_manifests/station_eligibility.csv` has 45 station/split rows; four stations have no test targets; each horizon's test scored-count sum equals 14,583.

## Limitations that verification does not remove

Weather archive release timestamps and station ingestion latencies are unavailable. The saved array's test period was previously inspected. Training input pollutant histories are heavily imputed; missingness and observed target distribution shift across splits. No new isolated-station fold or external city was evaluated. The directional hinge is not a conservation law. The selected λ reached 0.06, but directional and Laplacian penalties do not have matched effective magnitude or gradient. No code or metric check establishes causal atmospheric dependence, operational accuracy or road-node validity.

Archive CRC/member-hash verification and final remote-head equality are recorded separately after package creation and Git push. Large `partial.pt` restart files remain local and are listed by absolute path and SHA-256 in the package manifest; selected `best.pt` checkpoints and raw predictions are included in the package.
