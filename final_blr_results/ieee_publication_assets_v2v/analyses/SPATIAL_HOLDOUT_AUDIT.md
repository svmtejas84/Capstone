# Station-isolated paired-error audit

## Population and protocol

The corrected station-isolated evaluation has 15 mapped stations, 11 with observed targets and four with no scored test outcomes. It uses 14,583 matched observed station-time targets. Saved model output rows show the held-out site pollutant history was suppressed in the source forecaster input pathway; reproducing an absent fold checkpoint is not available. Site, not timestamp, is the independent spatial resampling unit.

## Main comparison and anchor alignment

The saved pooled result is ST-PIGNN MAE **22.3143 µg/m³** and weather/static ridge MAE **20.6241 µg/m³** (same target pairs; pooled difference +1.6902). The comparison is not an identical-anchor architecture ablation: ST-PIGNN uses a `train_mean` residual anchor and the ridge baseline output is recorded with `baseline` reconstruction. Neither score uses seasonal-bias-corrected rows. The common target population and no-bias-correction filter match; the output reconstruction mechanisms do not. Caption/table notes now state this distinction.

| Site | Pairs | ST-PIGNN MAE | Ridge MAE | Difference (ST-PIGNN − ridge) | Site winner |
|---:|---:|---:|---:|---:|---|
| 5607 | 1,620 | 12.488 | 21.546 | −9.058 | ST-PIGNN |
| 6973 | 302 | 18.217 | 11.076 | +7.141 | Ridge |
| 6974 | 8 | 3.893 | 14.118 | −10.225 | ST-PIGNN; only 8 targets |
| 6983 | 1,901 | 16.603 | 16.774 | −0.171 | ST-PIGNN |
| 6984 | 1,877 | 22.728 | 20.419 | +2.310 | Ridge |
| 3409385 | 2,113 | 53.373 | 41.646 | +11.726 | Ridge; influential site |
| 3409388 | 2,243 | 6.862 | 7.030 | −0.168 | ST-PIGNN |
| 3409393 | 2,207 | 17.717 | 21.391 | −3.674 | ST-PIGNN |
| 6119271 | 845 | 24.978 | 17.455 | +7.523 | Ridge |
| 6146655 | 212 | 23.833 | 20.806 | +3.027 | Ridge |
| 6206921 | 1,255 | 25.494 | 17.569 | +7.925 | Ridge |

Five sites favor ST-PIGNN and six favor ridge. Station 3409385 contributes a large paired disadvantage to ST-PIGNN; site 6974 has too few points to support a stable local conclusion.

## Uncertainty with stations as sites

- Equal-station mean paired difference: **+1.4869 µg/m³**; 20,000-resample station-bootstrap 95% CI **[−2.5765, +5.3278]**, seed 8127.
- Nested site-then-seven-calendar-day-block sensitivity: pooled paired difference **+1.4869 µg/m³**; 2,000-resample 95% interval **[−2.5449, +6.6022]**, seed 9131. Each bootstrap samples eleven sites with replacement, then contiguous seven-day calendar blocks within each sampled site's observed period; empty site-days remain empty.

The intervals are broad and include zero. The pooled test comparison favors ridge, while the equal-site point estimate also favors ridge; uncertainty and heterogeneity do not support a claim that ST-PIGNN loses at every station. Full per-pair source and station-level derived table: `source_data/F05_station_time_paired_errors.csv`, `source_data/F05_station_paired_errors.csv`, and `source_data/F05_bootstrap_intervals.csv`.

## Decoder results are a separate estimand

The forecast-origin-safe decoder evaluation uses the same 14,583 target pairs across eleven held-out sites, but a separate cross-fitted source-forecast/decoder pipeline. Pooled MAE: decoder 27.3599, forecast-IDW 20.1536, training-derived station mean 20.6338 µg/m³. Decoder minus forecast-IDW is +7.2063 µg/m³ pooled. Equal-site difference is +5.1008 µg/m³ (station-bootstrap 95% CI [+1.8146,+8.3013], eleven sites, 2,000 resamples). Pooled weighting and equal-site averaging answer different questions and are not contradictory.
