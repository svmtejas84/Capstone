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
