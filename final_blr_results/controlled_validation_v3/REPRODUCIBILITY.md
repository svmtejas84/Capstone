# Controlled validation v3 — reproduction and recovery

Repository root: `/home/jupyter-1nt23cb058/Capstone`. Branch: `research/controlled-validation-v3`. The original protocol SHA-256 is `00b5e2215a5c6017493ae256e3f8e350df66d1f76084c59efc1db36213ab2675`; it was committed and pushed before new fits. Read `PROTOCOL_AMENDMENT_01.md`, `PROTOCOL_AMENDMENT_02.md`, and `STATISTICAL_PLAN_ADDENDUM.md` before interpreting the outputs. The repaired data-array SHA-256 is `bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202`. All source hash records are in `data_manifests/source_checksums.csv`.

## Environment

- NVIDIA Tesla V100-PCIE-32GB (32,768 MiB); Python 3.9.7; Linux 5.15; PyTorch 2.8.0+cu128; PyTorch Geometric 2.6.1; NumPy 1.26.4; pandas 2.3.3; SciPy 1.13.1; scikit-learn 1.6.1; Matplotlib 3.9.4.
- The command sandbox may hide CUDA even though the JupyterHub host has the V100. GPU stages used approved elevated execution and `scripts/run_supervised.sh`; sandboxed `nvidia-smi`/CUDA failure is not a missing-hardware verdict.
- `pandas.DataFrame.to_latex()` cannot run with the host's Jinja2 3.0.3, so `scripts/build_results.py` uses a deterministic direct LaTeX tabular writer. No dependency was upgraded during this campaign.

## Saved-data and no-training verification

From the repository root:

```bash
PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/verify_training.py
PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/verify_baselines.py final
PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/verify_results.py
```

The first verifier checks 20 valid regularizer selection plus 125 regularizer final checkpoint records. The second checks 120 baseline selection plus 150 baseline final records, including model identity, chosen validation LR, epochs, array/checkpoint hashes. The third recalculates every saved metric from paired raw prediction NPZ files and all 20 frozen contrasts from those files; it also checks seven historical input hashes and exact target alignment. All 355 metric rows and 20 contrast rows passed in the completed campaign. It does not rerun model inference.

To regenerate derived descriptive products from saved predictions without training or retuning:

```bash
PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/summarize_training.py
PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/data_summary.py
PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/station_eligibility.py
PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/analyze_controls.py
PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/secondary_diagnostics.py
PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/wind_cone_diagnostics.py
PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/build_results.py
```

The exposed historical test was unlocked once at `verification/test_unlock.json`. Do not call `evaluate_controls.py` or `evaluate_baselines.py` for ordinary regeneration: the saved `predictions/*.npz` are sufficient and prevent repeated test-inference passes. The evaluation drivers support recovery after an interrupted first pass by reusing atomically saved seed predictions; complete `metrics/matched_controls.csv` and `metrics/baselines.csv` now exist. The two supervised scorer logs and completion markers are under `logs/test_controls/` and `logs/test_baselines/`.

## Artifact semantics

- `data_manifests/data_v3_causal_arrays.npz`: versioned delayed-pollutant array; its observed targets/masks were not moved. `data_manifests/source_checksums.csv` records the original array and source code hashes.
- `data_manifests/station_eligibility.csv`: all 15 station IDs for each of the three chronological splits, observed target counts, input missingness and scored eligibility at each horizon. Four stations have no exposed-test targets.
- `training/final/h{h}_seed{s}_{variant}/best.pt`: selected regularizer checkpoint; each cell has `COMPLETE.json`, `epochs.json`, and restart-only `partial.pt`. `training/baselines/{model}/final/h{h}_seed{s}/` is analogous. Selection-stage cells are separate. `training/invalidated_pre_causal_shift/` contains the quarantined failed-protocol attempts; none entered the final metrics.
- `predictions/h{h}_{variant}_seed{s}.npz`, `..._ensemble.npz`, and analogous baseline files: raw PM2.5 predictions, observed truths, target time indices and station indices. Every horizon uses 14,583 scored station-hour pairs. The ensemble averages raw seed predictions before scoring.
- `metrics/matched_controls.csv`, `metrics/baselines.csv`: primary per-seed and ensemble MAE/RMSE/R². `statistical_analysis/primary_contrasts.csv`: frozen 20 ensemble pair comparisons. `metrics/per_station_descriptive.csv` is temporal per-station reporting, not a held-out-site experiment. `metrics/wind_cone_diagnostics.csv` is descriptive station-space ordering, not conservation.
- `metrics/T1_*.csv` through `T8_*.csv` and companion `.tex`; `figures/F1_*.{png,pdf,svg}` through `F6_*`: derived presentation files. F7 spatial holdout is explicitly **NOT EVALUATED** in `metrics/T7_SPATIAL_HOLDOUT.csv`.
- `verification/results_verification.json`, `verification/full_future_mutation.json`, `verification/smoke_gpu.json`, `logs/` and `metrics/resource_usage.csv`: integrity, leakage and compute evidence.

The final ZIP includes `best.pt` selected checkpoints and the complete saved-prediction arrays. Restart-only `partial.pt` tensors remain local and are listed with absolute paths and SHA-256 in `verification/local_checkpoint_manifest.csv`. The ZIP is a local supplemental backup, not an independently verified USB copy. The historical test and weather-release limitations remain even if all commands reproduce exactly.
