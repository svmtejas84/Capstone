# Residual h=1 gate

Source: `scripts/summarize_gate_v2c.py`, `configs/gate_v2c.yaml`, seeds [11, 23, 37, 51, 79], commit `012ace70c44dd9167595dfe1219914f97bc0a6f2`, 2026-10-25T04:02:55.366450+00:00. All test rows use the same 14583 observed station-hour pairs.

| Method | Selection | Seeds | MAE mean±SD (µg/m³) | R² mean±SD |
|---|---|---:|---:|---:|
| persistence | classical | 0 | 8.116095 | 0.532089 |
| climatology_hod_dow | classical | 0 | 21.468647 | -0.092450 |
| station_train_mean | classical | 0 | 20.964647 | -0.014396 |
| idw_known_at_t | classical | 0 | 22.698642 | -0.205856 |
| ridge_meteorology_static | classical | 0 | 20.518614 | 0.057021 |
| gru_only | validation | 5 | 8.330855±0.155887 | 0.545433±0.014658 |
| st_gru_gcn | validation | 5 | 8.430984±0.019712 | 0.533563±0.006226 |
| stpignn_corrected | validation | 5 | 8.259108±0.185399 | 0.593407±0.002134 |
| stpignn_laplacian | validation | 5 | 8.282859±0.242948 | 0.591132±0.006408 |
| vanilla_gcn | validation | 5 | 8.347697±0.062389 | 0.531393±0.004632 |
| gru_only | train_tail | 5 | 8.355098±0.211010 | 0.543281±0.018363 |
| st_gru_gcn | train_tail | 5 | 8.446902±0.152493 | 0.525269±0.009380 |
| stpignn_corrected | train_tail | 5 | 8.273430±0.109027 | 0.582991±0.002747 |
| stpignn_laplacian | train_tail | 5 | 8.523304±0.289167 | 0.590410±0.003886 |
| vanilla_gcn | train_tail | 5 | 8.353007±0.061918 | 0.529853±0.004671 |

Classical validation selection (not test selection):

| Method | Validation pairs | MAE | R² |
|---|---:|---:|---:|
| climatology_hod_dow | 7203 | 9.305324 | 0.073334 |
| ridge_meteorology_static | 7203 | 10.367326 | -0.057493 |
| idw_known_at_t | 7203 | 12.645726 | -0.522832 |

Corrected ST-PIGNN selected by validation: seed 11, LR 0.003, selection MAE 3.142210, test MAE 8.401826, R² 0.589756.

| ST-PIGNN minus reference | MAE difference [95% UTC-day CI] | R² difference [95% UTC-day CI] |
|---|---:|---:|
| persistence | 0.285730 [0.183806, 0.393342] | 0.057667 [0.044899, 0.070625] |
| climatology_hod_dow | -13.066822 [-13.861912, -12.262534] | 0.682206 [0.634023, 0.735647] |

Corrected ST-PIGNN selected by train_tail: seed 11, LR 0.0001, selection MAE 4.077200, test MAE 8.127372, R² 0.578965. Original July–September validation MAE (diagnostic only): 3.260932.

Validation-selected residual ST-PIGNN beats persistence on test MAE with paired CI excluding zero: NO.
source: results/gate_v2c.csv, results/gate_v2c_bootstrap.json, results/classical_validation_v2c.csv; produced by scripts/summarize_gate_v2c.py.
