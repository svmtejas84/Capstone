# Persistence gate

All methods use raw observed PM2.5 at the same test station-hour pairs. ST-PIGNN row is the variant and seed selected by validation MAE.

| Method | Test pairs | MAE (µg/m³) | RMSE (µg/m³) | R² |
|---|---:|---:|---:|---:|
| Persistence | 14623 | 21.261102 | 177.317266 | -0.192012 |
| Hour/day climatology | 14623 | 392.031114 | 536.533600 | -9.913710 |
| ST-PIGNN stpignn_corrected_imputed, seed 37 | 14623 | 30.584854 | 161.285796 | 0.013787 |

| Paired difference: ST-PIGNN minus baseline | MAE difference and 95% day-bootstrap CI (µg/m³) | R² difference and 95% CI |
|---|---:|---:|
| Persistence | 9.323752 [7.535600, 10.784741] | 0.205799 [0.047942, 0.419453] |
| Hour/day climatology | -361.446260 [-381.058161, -341.263092] | 9.927497 [6.257045, 20.146302] |

Point-metric gate: FAIL. CI-supported gate: FAIL.

source: results/gate_bootstrap_v2.json, results/neural_final_v2.csv, results/neural_predictions_v2.parquet, results/baselines_v2_metrics.csv; produced by scripts/summarize_gate_v2.py; configs/gate_v2.yaml and data_v2.yaml; seed and git commit and UTC timestamp in gate_bootstrap_v2.json.
