# Spatial validation

W6 corrected LOSO: 11 scored stations, four unscored (5547, 5548, 6975, 2498781), 14,583 repeated pairs. ST-PIGNN MAE 22.314 versus weather/static ridge 20.624 µg/m³; station is the spatial unit, not timestamp.

v2o IDW was retrospective same-hour spatial reconstruction, not positive-lead forecasting: IDW scored 12,328/14,583 pairs and did not improve on train-only mean. v2r evaluated same-origin six-hour forecasts with 15 outer station-isolated folds plus time-block cross-fitting; 11 sites/14,583 pairs. Train-only mean MAE 20.634, forecast-IDW 20.154, decoder 27.360 µg/m³. Decoder lost to both controls at 9/11 sites. No roadside independent truth. Preserve populations and tasks separately.
