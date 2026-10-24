# Cleaned h=1 gate

All rows use the same observed test station-hours. Neural entries are five-seed means and sample SDs; the 20-epoch entries are separate budget diagnostics.

| Method | Budget | Seeds | Pairs | MAE mean±SD (µg/m³) | RMSE mean±SD (µg/m³) | R² mean±SD |
|---|---|---:|---:|---:|---:|---:|
| persistence | baseline | 0 | 14583 | 8.116095 | 25.357742 | 0.532089 |
| climatology_hod_dow | baseline | 0 | 14583 | 21.468647 | 38.746251 | -0.092450 |
| idw_known_at_t | baseline | 0 | 14583 | 22.698642 | 40.707692 | -0.205856 |
| ridge_meteorology_static | baseline | 0 | 14583 | 20.518614 | 35.998118 | 0.057021 |
| gru_only | short | 5 | 14583 | 20.564168±0.091654 | 36.884085±0.782157 | 0.009678±0.042200 |
| st_gru_gcn | short | 5 | 14583 | 21.235125±0.412892 | 37.119014±0.232065 | -0.002649±0.012521 |
| stpignn_corrected | short | 5 | 14583 | 20.723163±0.131595 | 36.904711±0.437938 | 0.008815±0.023338 |
| stpignn_laplacian | short | 5 | 14583 | 20.554820±0.029394 | 36.674745±0.389783 | 0.021151±0.020720 |
| vanilla_gcn | short | 5 | 14583 | 20.313571±0.122855 | 37.006464±0.156252 | 0.003439±0.008400 |
| gru_only | longer | 5 | 14583 | 20.125472±0.448876 | 36.790290±0.871987 | 0.014620±0.046923 |
| stpignn_corrected | longer | 5 | 14583 | 20.689290±0.219278 | 37.075091±0.358404 | -0.000321±0.019351 |

Validation-selected corrected ST-PIGNN (short): seed 23, LR 0.0003, scaler log1p, validation MAE 7.700626 µg/m³; test MAE 20.613632 µg/m³, R² 0.001594.

| Paired ST-PIGNN minus baseline | MAE difference [95% UTC-day CI], µg/m³ | R² difference [95% UTC-day CI] |
|---|---:|---:|
| persistence | 12.497537 [11.797404, 13.163366] | -0.530495 [-0.595027, -0.466313] |
| idw_known_at_t | -2.085010 [-3.013297, -1.192179] | 0.207449 [0.153649, 0.261566] |

Validation-selected corrected ST-PIGNN (longer): seed 37, LR 0.0003, scaler log1p, validation MAE 6.741038 µg/m³; test MAE 20.540100 µg/m³, R² -0.028360.

| Paired ST-PIGNN minus baseline | MAE difference [95% UTC-day CI], µg/m³ | R² difference [95% UTC-day CI] |
|---|---:|---:|
| persistence | 12.424005 [11.693315, 13.134217] | -0.560449 [-0.624162, -0.496925] |
| idw_known_at_t | -2.158541 [-3.080338, -1.233524] | 0.177495 [0.125794, 0.233093] |

Primary matched-budget corrected ST-PIGNN beats persistence and IDW on test MAE and R²: NO; paired bootstrap CIs support both comparisons: NO.

source: results/gate_v2b.csv and results/gate_v2b_bootstrap.json; produced by scripts/summarize_gate_v2b.py; config configs/gate_v2b.yaml, seeds/commit/UTC timestamp in gate_v2b_bootstrap.json.
