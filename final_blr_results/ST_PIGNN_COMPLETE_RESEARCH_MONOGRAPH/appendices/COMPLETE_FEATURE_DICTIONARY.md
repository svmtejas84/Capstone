# Complete Feature Dictionary

This register reproduces the cited source records below, retaining their original protocol and status. Later source exhibits can supersede earlier conclusions; no incompatible populations are pooled.

## Source 1: `final_blr_results/city_scale/features/feature_registry.csv`

[EVIDENCE: `final_blr_results/city_scale/features/feature_registry.csv` | SHA-256 `95635264557e2af0592731faf06e72b862666cec31fb596782a76baa3ea09d4f` | snapshot `1c46a4b`]

Rows: 18. Columns: 7. Units, population and protocol are those declared by the source columns or its methodology.

| index | station_feature | physical_unit | station_preprocessing | road_counterpart | road_citywide_coverage | compatibility |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | pm25_lagged | ug/m3 | train-fitted standardized log1p and causal imputation | station_pm25 | no | BLOCKED |
| 1 | pm10 | ug/m3 | train-fitted standardized log1p and causal fill | station_pm10 | no | BLOCKED |
| 2 | no2 | ppb | train-fitted z-score and causal fill | station_no2 | no | BLOCKED |
| 3 | so2 | ppb | train-fitted z-score and causal fill | station_so2 | no | BLOCKED |
| 4 | co | ppb | train-fitted z-score and causal fill | station_co | no | BLOCKED |
| 5 | wind_speed | m/s | train-fitted z-score | weather_wind_speed_10m | no | BLOCKED |
| 6 | wind_gusts | m/s | train-fitted z-score | weather_wind_gusts_10m | no | BLOCKED |
| 7 | temperature | degC | train-fitted z-score | weather_temperature_2m | no | BLOCKED |
| 8 | humidity | percent | train-fitted z-score | weather_relative_humidity_2m | no | BLOCKED |
| 9 | surface_pressure | hPa | train-fitted z-score | weather_surface_pressure | no | BLOCKED |
| 10 | wind_direction_sin | unitless | train-fitted z-score of sine | weather_wind_direction_10m | no | BLOCKED |
| 11 | wind_direction_cos | unitless | train-fitted z-score of cosine | weather_wind_direction_10m | no | BLOCKED |
| 12 | srtm_elevation | m | train-fitted z-score | elevation | yes | APPROXIMATE WITH ASSUMPTIONS |
| 13 | lag_is_imputed | binary | raw missingness indicator | none | no | BLOCKED |
| 14 | hour_sin | unitless | raw calendar sine | none | derivable | APPROXIMATE WITH ASSUMPTIONS |
| 15 | hour_cos | unitless | raw calendar cosine | none | derivable | APPROXIMATE WITH ASSUMPTIONS |
| 16 | weekday_sin | unitless | raw calendar sine | none | derivable | APPROXIMATE WITH ASSUMPTIONS |
| 17 | weekday_cos | unitless | raw calendar cosine | none | derivable | APPROXIMATE WITH ASSUMPTIONS |

## Source 2: `final_blr_results/citywide_extension/v2o/ROAD_NODE_FEATURE_REGISTRY.csv`

[EVIDENCE: `final_blr_results/citywide_extension/v2o/ROAD_NODE_FEATURE_REGISTRY.csv` | SHA-256 `cb7eb571eba8f3b53d012461da2badd3a08677f1acb80f89e119a4780fc0cb79` | snapshot `1c46a4b`]

Rows: 14. Columns: 11. Units, population and protocol are those declared by the source columns or its methodology.

| feature | source | unit | spatial_resolution | temporal_resolution | kind | forecast_time_eligible | missingness | imputation | transformation | train_fitted_parameter |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| road_row_index | raw OSM node Parquet | index | road node | static | identifier | yes | none | none | none | none |
| osmid | raw OSM node Parquet | OSM ID | road node | static | identifier | yes | none | none | none | none |
| utm_x_m | raw OSM node Parquet | m | road node | static | geometry | yes | none | none | EPSG:32643 | none |
| utm_y_m | raw OSM node Parquet | m | road node | static | geometry | yes | none | none | EPSG:32643 | none |
| elevation_srtm_m | nodes_elevation_true.parquet | m | SRTM raster sampled at node | static | remote-sensing estimate | yes | none in canonical table | none | none | none |
| support_station_pm25 | cleaned v2m observed_target at same UTC hour | ug/m3 | monitor site | hourly | observation | no for future lead-time forecast | missing at unobserved station-hours | none | 0-500 cleaned observation | none |
| estimate_ug_m3 | fixed IDW power 2 from same-hour observed stations | ug/m3 | road node | selected UTC hour | model estimate | no for future lead-time forecast | unavailable if fewer than two support stations | none | Euclidean inverse-distance squared | none |
| nearest_support_distance_m | road geometry and eligible observed monitors | m | road node | selected UTC hour | support diagnostic | yes for geometry; eligible station set depends on same-hour data | unavailable with zero support | none | minimum Euclidean distance | none |
| support_station_count | observed station mask at selected hour | count | city support set | selected UTC hour | support diagnostic | no for future lead-time forecast | none | none | count | none |
| outside_support_hull | convex hull of same-hour eligible monitors | binary | road node | selected UTC hour | support diagnostic | no for future lead-time forecast | unavailable for degenerate hull | none | Delaunay hull membership | none |
| poor_support | outside hull or distance greater than 5000 m | binary | road node | selected UTC hour | map display flag | no for future lead-time forecast | none | none | predeclared display rule | none |
| road_pm25_observed | unavailable | ug/m3 | road node | hourly | missing | no | all unsensed road nodes | none | none | none |
| road_pm25_lag | unavailable | ug/m3 | road node | hourly | missing | no | all unsensed road nodes | none | none | none |
| road_wind_differentiated | unavailable | m/s or degree | road node | hourly | missing | no | all road nodes | none | none | none |

## Source 3: `final_blr_results/baselines/v2m/methodology/weather_availability_audit.csv`

[EVIDENCE: `final_blr_results/baselines/v2m/methodology/weather_availability_audit.csv` | SHA-256 `7c5353edbbfbf655671f017e907460ffca786d48099861ce63932802e352eb38` | snapshot `1c46a4b`]

Rows: 5. Columns: 11. Units, population and protocol are those declared by the source columns or its methodology.

| horizon_hours | target_pairs | unique_target_hours | earliest_cutoff_utc | latest_cutoff_utc | pairs_with_record_after_cutoff | pairs_with_future_temperature_used | pairs_with_all_six_future_weather_values | future_temperature_fraction | model_input_last_hour | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 14583 | 4063 | 2025-09-22 23:00:00+00:00 | 2026-03-28 22:00:00+00:00 | 14563 | 14563 | 14563 | 0.9986285400809162 | cutoff | Open-Meteo Archive API; scripts/pull_weather.py |
| 3 | 14583 | 4063 | 2025-09-22 21:00:00+00:00 | 2026-03-28 20:00:00+00:00 | 14571 | 14571 | 14571 | 0.9991771240485496 | cutoff | Open-Meteo Archive API; scripts/pull_weather.py |
| 6 | 14583 | 4063 | 2025-09-22 18:00:00+00:00 | 2026-03-28 17:00:00+00:00 | 14583 | 14583 | 14583 | 1.0 | cutoff | Open-Meteo Archive API; scripts/pull_weather.py |
| 12 | 14583 | 4063 | 2025-09-22 12:00:00+00:00 | 2026-03-28 11:00:00+00:00 | 14583 | 14583 | 14583 | 1.0 | cutoff | Open-Meteo Archive API; scripts/pull_weather.py |
| 24 | 14583 | 4063 | 2025-09-22 00:00:00+00:00 | 2026-03-27 23:00:00+00:00 | 14583 | 14583 | 14583 | 1.0 | cutoff | Open-Meteo Archive API; scripts/pull_weather.py |
