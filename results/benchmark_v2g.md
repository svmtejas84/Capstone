# Benchmark v2g

Source `scripts/summarize_benchmark_v2g.py`, `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], commit `d2ce207be6754cf40f8662eb7ccd33b7128e3e04`, 2026-10-25T09:32:39.915124+00:00.

| h (hours) | Model | Test pairs | MAE (µg/m³) | R² |
|---:|---|---:|---:|---:|
| 1 | adaptive_graph_st | 14583 | 8.025968 | 0.543357 |
| 1 | adaptive_graph_st_fixed_knn | 14583 | 8.068487 | 0.584257 |
| 1 | climatology_hod_dow | 14583 | 21.468647 | -0.092450 |
| 1 | gine_gru_wind | 14583 | 8.056366 | 0.547921 |
| 1 | gru_only | 14583 | 8.054509 | 0.573718 |
| 1 | persistence | 14583 | 8.116095 | 0.532089 |
| 1 | ridge_lag_calendar_weather | 14583 | 8.691828 | 0.566312 |
| 1 | same_hour_yesterday | 14583 | 14.130312 | 0.283173 |
| 1 | st_gru_gcn | 14583 | 8.243261 | 0.543516 |
| 1 | station_train_mean | 14583 | 20.964647 | -0.014396 |
| 1 | stpignn_lambda0 | 14583 | 8.034619 | 0.578618 |
| 1 | stpignn_laplacian | 14583 | 8.035369 | 0.587342 |
| 1 | stpignn_original | 14583 | 8.018825 | 0.585597 |
| 1 | stpignn_v2 | 14583 | 9.320887 | 0.546394 |
| 1 | stpignn_v2_source_removed | 14583 | 9.315458 | 0.545785 |
| 1 | stpignn_v2_transport_removed | 14583 | 8.056361 | 0.547925 |
| 1 | vanilla_gcn | 14583 | 8.489067 | 0.537234 |

## Fixed criteria

h=1, gine_gru_wind: met; persistence ΔMAE -0.059730 CI [-0.093491,-0.024862]; same_hour_yesterday ΔMAE -6.073946 CI [-6.836922,-5.314510].
h=1, adaptive_graph_st: met; persistence ΔMAE -0.090127 CI [-0.111708,-0.068875]; same_hour_yesterday ΔMAE -6.104344 CI [-6.867843,-5.345048].
h=1, stpignn_v2: not met; persistence ΔMAE +1.204792 CI [+0.956397,+1.459631]; same_hour_yesterday ΔMAE -4.809425 CI [-5.607807,-4.071090].
h=1, stpignn_original: not met; persistence ΔMAE -0.097270 CI [-0.202529,+0.004498]; same_hour_yesterday ΔMAE -6.111487 CI [-6.849143,-5.375730].
h=1, C vs stpignn_v2_source_removed: not met; ΔMAE +0.005429 CI [-0.058597,+0.069472]; ΔR² +0.000609 CI [-0.006059,+0.007582].
h=1, C vs stpignn_v2_transport_removed: not met; ΔMAE +1.264526 CI [+1.025528,+1.506480]; ΔR² -0.001531 CI [-0.021365,+0.018076].
h=1, C vs stpignn_lambda0: not met; ΔMAE +1.286268 CI [+1.075846,+1.503703]; ΔR² -0.032223 CI [-0.047678,-0.016037].
h=1, C vs stpignn_laplacian: not met; ΔMAE +1.285519 CI [+1.081338,+1.494683]; ΔR² -0.040948 CI [-0.054925,-0.026608].

Any-model win: met.
C physics-in-architecture support: not met.
DEM criterion: not assessed by this script.
