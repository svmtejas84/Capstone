# v2r spatial validation verdict

## Protocol and population

Exploratory six-hour station-isolated LOSO evaluation on the corrected 15-station graph. Forecast inputs ended at target minus six hours. Fifteen outer folds were fit; each held-out station was removed from pollutant inputs, target fitting, anchor construction, and preprocessing. For decoder fitting, support forecasts came from the time-block cross-fit models fitted through 2025-01-30 and forecast for 2025-04-02 through 2025-06-29. Decoder model selection used the 2025-07-01 through 2025-09-21 validation period. Test targets were not used for fit or model selection. All Bengaluru results remain exploratory because this dataset and test period have been repeatedly examined.

Four station folds had no eligible test targets; the scored evaluation contains 11 station sites and 14,583 station-time pairs. The same pairs were used by all three methods. Confidence intervals resample the 11 sites equally, not the timestamps.

## Pooled comparison

| Method | MAE (µg/m³) | RMSE (µg/m³) | R² | Coverage | Sites |
|---|---:|---:|---:|---:|---:|
| Training-only station mean | 20.634 | 38.614 | −0.085 | 14,583/14,583 | 11 |
| Six-hour station forecasts + p=2 IDW | **20.154** | 39.295 | −0.124 | 14,583/14,583 | 11 |
| Six-hour station forecasts + learned decoder | 27.360 | 44.046 | −0.412 | 14,583/14,583 | 11 |

The decoder (1,249 parameters) had higher MAE than IDW at 9/11 scored stations and higher MAE than the station-mean control at 9/11. Equal-site mean paired MAE differences (decoder minus control) were +5.101 µg/m³ versus IDW (station-bootstrap 95% CI +1.815 to +8.302) and +5.939 versus the mean (+2.514 to +9.379). These descriptive intervals do not establish population-level inference with eleven exposed Bengaluru sites. Per-station MAE, RMSE, R² and counts are in `../spatial_decoder/per_station_test_metrics.csv`; paired intervals are in `../spatial_decoder/station_bootstrap_comparisons.csv`; raw predictions are in `../spatial_decoder/folds/all_spatial_test_predictions.parquet`.

The simple forecast-IDW baseline is the strongest of the three on pooled MAE. IDW and the decoder do not improve consistently over the training-only station mean. All pooled R² values are negative. This does not support citywide road accuracy.

## Provenance and limitations

All support values are corrected GINE–GRU h=6 predictions made at the corresponding issue time; support forecasts used for test targets came from the outer fold excluding the query station. The decoder was trained only on cross-fitted forecast examples, uses fixed projected distances and verified SRTM elevation, and was selected by validation MAE. No held-out target enters a support forecast or decoder fit. Four unscored stations remain unscored rather than removed from the register. The number of independent spatial test sites is eleven, not 14,583.

Structural validity of the separate road graph is not evidence of spatial prediction accuracy. No independent road-side observations were available. Preserve earlier W6 LOSO (ST-PIGNN MAE 22.314 vs weather/static ridge 20.624) and v2o retrospective IDW findings; those use different populations/protocols and are not pooled here.
