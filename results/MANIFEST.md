# Phase A evidence artifacts

Generated on branch `audit/canonical-notebook-20261023` from source commit `22a0f5ac5a0527bf173e97692e22c20a245bc6a7`. Configuration: `configs/audit_canonical.yaml`; seed 42. Each JSON records its precise UTC run timestamp. Input data and checkpoint are existing repository workspace artifacts and are not copied here.

| File | Producer | Content |
|---|---|---|
| `audit_canonical.json` | `scripts/audit_canonical.py` | Checkpoint, graph, time split, station, elevation, PM2.5 tier and routing-field measurements |
| `audit_imputation_tiers.csv` | `scripts/audit_canonical.py` | All master rows by year, station ID and tier; includes non-PM2.5 pollutants |
| `stations.csv` | `scripts/audit_canonical.py` | Model-input station/node mapping, coordinates, saved partition cluster, nonzero scored targets and independently confirmed observed PM2.5 hours |
| `replay_canonical.json` | `scripts/replay_canonical.py` | Independent checkpoint MAE, RMSE, median AE, scored pairs, PVR and prediction summary |
| `replay_canonical.log` | `scripts/replay_canonical.py` | Raw notebook cell execution output, including progress and counters |
| `refactor_parity.json` | `scripts/check_canonical_refactor_parity.py` | Fixed-batch equality for extracted dataset, mask, penalty and metrics |

The replay executes selected canonical notebook cells without training or notebook figure/output cells. It reproduces the original data path and checkpoint but is not an observed-only or leak-free evaluation.

## Rebuilt data and persistence gate

These files were generated on branch `audit/canonical-notebook-20261023` with `configs/data_v2.yaml` and `configs/gate_v2.yaml`. Each associated `*_run.json`, `data_v2_fit.json`, `feature_registry.json` or `gate_bootstrap_v2.json` records its source git commit, script, seed and UTC timestamp. The precise run provenance is also listed in `claude_paper.md` section 0.

| File | Producer | Content |
|---|---|---|
| `data_v2_arrays.npz`, `data_v2_fit.json`, `feature_registry.json`, `splits_v2.json` | `scripts/build_data_v2.py` | Aligned hourly tensors, train-fitted statistics, unique feature order and split counts |
| `stations_v2.csv`, `imputation_breakdown_v2.csv` | `scripts/build_data_v2.py` | Station mapping and per-station/year/tier provenance |
| `data_v2_diagnostics.json` | `scripts/diagnose_data_v2.py` | Raw row counts, target distribution, train-only scale diagnostics |
| `physics_v2_mask_summary.json`, `wind_mask_coverage_v2.csv` | `scripts/analyze_physics_v2.py` | Legacy versus corrected wind-mask coverage |
| `baselines_v2_predictions.parquet`, `baselines_v2_metrics.csv`, `baselines_v2_run.json` | `scripts/evaluate_baselines_v2.py` | Common-mask classical baseline predictions, pooled and per-station metrics |
| `neural_selection_v2.csv`, `neural_selection_initial_run.json`, `neural_selection_run.json` | `scripts/train_gate_v2.py --stage selection` | Validation-only learning-rate and target-scaler sweep |
| `neural_final_v2.csv`, `neural_predictions_v2.parquet`, `neural_curves_v2.csv`, `neural_final_run.json`, `checkpoints_v2/` | `scripts/train_gate_v2.py --stage final` | Five-seed trained scores, per-pair predictions, learning curves and checkpoints |
| `neural_summary_v2.csv`, `neural_per_station_v2.csv`, `gate_bootstrap_v2.json`, `gate_persistence.md` | `scripts/summarize_gate_v2.py` | Five-seed summary, station metrics and paired day-bootstrap gate |
| `legacy_checkpoint_v2_predictions.parquet`, `legacy_checkpoint_v2_metrics.csv`, `legacy_checkpoint_v2_run.json` | `scripts/evaluate_legacy_checkpoint_v2.py` | Diagnostic old-checkpoint adapter on rebuilt observed test targets |
| `pvr_gate_v2.csv`, `pvr_gate_v2_run.json` | `scripts/evaluate_pvr_gate_v2.py` | Test PVR for corrected and legacy masks, all trained seeds and thresholds without Q |

The gate failed because the validation-selected ST-PIGNN had higher test MAE than persistence. Q results are blocked by an absent measured traffic index. The old-checkpoint adapter changes both graph and feature construction, so its score is diagnostic only.
