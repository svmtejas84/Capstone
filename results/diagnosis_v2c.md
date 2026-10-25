# S1 diagnosis

Source: `scripts/diagnose_v2c.py`, `configs/data_v2.yaml`, `configs/gate_v2b.yaml`, seed 42, checkpoint seeds [11, 23, 37, 51, 79], commit `38f477f4ae4b11824ee0405fe6e33a3940ba5d76`, 2026-10-25T02:43:01.533108+00:00.

| Split | Observed pairs | Target mean | Median | SD | Lag–target r | Lag MAE | Lag p99 | Lag max | Lag >500 | Immediate observed lag pairs | Immediate-lag r | Persistence MAE | Persistence R² |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 32628 | 34.139526 | 31.000000 | 22.995157 | 0.040120 | 9.665841 | 100.993169 | 44428.417969 | 3 | 30974 | 0.823055 | 5.482564 | 0.624062 |
| validation | 7203 | 24.969522 | 25.817499 | 12.810345 | 0.832708 | 3.312929 | 62.999600 | 154.962494 | 0 | 6965 | 0.854656 | 3.071653 | 0.699604 |
| test | 14583 | 44.425632 | 36.340000 | 37.070534 | 0.732890 | 8.608278 | 200.728924 | 930.041199 | 2 | 14079 | 0.784410 | 8.116095 | 0.532089 |

Lag network input uses train-fitted raw standardization: feature mean 39.169331, SD 562.017334. Neural targets use train-fitted log1p standardization: log mean 3.380092, log SD 0.639000. These are different transforms.

| Test train-only regression | MAE | R² |
|---|---:|---:|
| ar_lag | 20.562207 | -0.073372 |
| ridge_lag_weather_static | 20.485240 | 0.059078 |

| Model | Validation MAE | Test MAE | Test minus validation MAE |
|---|---:|---:|---:|
| gru_only | 8.711073 | 20.564168 | 11.853095 |
| st_gru_gcn | 9.251856 | 21.235125 | 11.983270 |
| stpignn_corrected | 7.807736 | 20.723163 | 12.915427 |
| stpignn_laplacian | 7.886274 | 20.554820 | 12.668546 |
| vanilla_gcn | 9.061305 | 20.313571 | 11.252265 |

| Saved model | Seed | Prediction–lag r | Lag-explained prediction variance |
|---|---:|---:|---:|
| stpignn_corrected | 11 | 0.319891 | 0.102330 |
| stpignn_corrected | 23 | 0.275416 | 0.075854 |
| stpignn_corrected | 37 | 0.338096 | 0.114309 |
| stpignn_corrected | 51 | 0.341434 | 0.116577 |
| stpignn_corrected | 79 | 0.304672 | 0.092825 |
| gru_only | 11 | 0.189508 | 0.035913 |
| gru_only | 23 | 0.193688 | 0.037515 |
| gru_only | 37 | 0.271808 | 0.073880 |
| gru_only | 51 | 0.267729 | 0.071679 |
| gru_only | 79 | 0.287141 | 0.082450 |

| Unscored LOSO station | Train observed targets | Validation | Test |
|---|---:|---:|---:|
| 5547 | 2589 | 0 | 0 |
| 5548 | 2 | 0 | 0 |
| 6975 | 2563 | 0 | 0 |
| 2498781 | 9278 | 0 | 0 |

AR intercept 34.052818, slope 0.002297; Ridge alpha 1.0, lag plus weather/static indices [0, 5, 6, 7, 8, 9, 10, 11, 12].

Checkpoint prediction–lag correlation and explained variance: source `results/diagnosis_checkpoints_v2c.csv`.
Model validation–test MAE gaps: source `results/diagnosis_model_gap_v2c.csv`.
Four LOSO station split counts: source `results/diagnosis_unscored_stations_v2c.csv`.

Persistence test minus validation MAE: 5.044442 µg/m³.
Finding: lag input and neural target use different scaling transforms; formulation mismatch found.
Finding: the train lag channel contains values above the 500 µg/m³ target cleaning cap, with a near-zero all-pair correlation but high observed-immediate-lag correlation; imputation and scaling defect found. No timestamp shift was identified.
Finding: train-only AR and Ridge do not approach persistence on test; the imputed lag tail contaminates their training fits, so these results do not establish a timestamp-alignment defect.
Finding: four LOSO folds have zero observed test targets, so their absence is a coverage limitation.
