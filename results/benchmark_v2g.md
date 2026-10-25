# Benchmark v2g

Source `scripts/summarize_benchmark_v2g.py`, `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], commit `a2596c8f6e33fe8a2a0ab049d1b3f6611642b674`, 2026-10-25T09:51:10.688656+00:00.

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
| 6 | adaptive_graph_st | 14583 | 15.127259 | 0.125511 |
| 6 | adaptive_graph_st_fixed_knn | 14583 | 15.624989 | 0.097115 |
| 6 | climatology_hod_dow | 14583 | 21.468647 | -0.092450 |
| 6 | gine_gru_wind | 14583 | 15.780365 | 0.130968 |
| 6 | gru_only | 14583 | 15.191011 | 0.122186 |
| 6 | persistence | 14583 | 16.606891 | -0.161368 |
| 6 | ridge_lag_calendar_weather | 14583 | 15.814455 | 0.176952 |
| 6 | same_hour_yesterday | 14583 | 14.130312 | 0.283173 |
| 6 | st_gru_gcn | 14583 | 16.467911 | -0.074082 |
| 6 | station_train_mean | 14583 | 20.964647 | -0.014396 |
| 6 | stpignn_lambda0 | 14583 | 14.935553 | 0.159832 |
| 6 | stpignn_laplacian | 14583 | 14.894340 | 0.178884 |
| 6 | stpignn_original | 14583 | 14.840548 | 0.183055 |
| 6 | stpignn_v2 | 14583 | 16.406056 | 0.068911 |
| 6 | stpignn_v2_source_removed | 14583 | 16.476515 | 0.057444 |
| 6 | stpignn_v2_transport_removed | 14583 | 15.863768 | 0.117295 |
| 6 | vanilla_gcn | 14583 | 16.496535 | -0.122987 |

## Fixed criteria

h=1, gine_gru_wind: met; persistence ΔMAE -0.059730 CI [-0.093491,-0.024862]; same_hour_yesterday ΔMAE -6.073946 CI [-6.836922,-5.314510].
h=1, adaptive_graph_st: met; persistence ΔMAE -0.090127 CI [-0.111708,-0.068875]; same_hour_yesterday ΔMAE -6.104344 CI [-6.867843,-5.345048].
h=1, stpignn_v2: not met; persistence ΔMAE +1.204792 CI [+0.956397,+1.459631]; same_hour_yesterday ΔMAE -4.809425 CI [-5.607807,-4.071090].
h=1, stpignn_original: not met; persistence ΔMAE -0.097270 CI [-0.202529,+0.004498]; same_hour_yesterday ΔMAE -6.111487 CI [-6.849143,-5.375730].
h=1, C vs stpignn_v2_source_removed: not met; ΔMAE +0.005429 CI [-0.058597,+0.069472]; ΔR² +0.000609 CI [-0.006059,+0.007582].
h=1, C vs stpignn_v2_transport_removed: not met; ΔMAE +1.264526 CI [+1.025528,+1.506480]; ΔR² -0.001531 CI [-0.021365,+0.018076].
h=1, C vs stpignn_lambda0: not met; ΔMAE +1.286268 CI [+1.075846,+1.503703]; ΔR² -0.032223 CI [-0.047678,-0.016037].
h=1, C vs stpignn_laplacian: not met; ΔMAE +1.285519 CI [+1.081338,+1.494683]; ΔR² -0.040948 CI [-0.054925,-0.026608].
h=6, gine_gru_wind: not met; persistence ΔMAE -0.826526 CI [-1.303282,-0.359625]; same_hour_yesterday ΔMAE +1.650053 CI [+0.863279,+2.480145].
h=6, adaptive_graph_st: not met; persistence ΔMAE -1.479632 CI [-1.914625,-1.001425]; same_hour_yesterday ΔMAE +0.996947 CI [+0.176091,+1.828676].
h=6, stpignn_v2: not met; persistence ΔMAE -0.200835 CI [-0.610891,+0.203061]; same_hour_yesterday ΔMAE +2.275745 CI [+1.370734,+3.191583].
h=6, stpignn_original: not met; persistence ΔMAE -1.766343 CI [-2.219745,-1.288067]; same_hour_yesterday ΔMAE +0.710236 CI [-0.068723,+1.500975].
h=6, C vs stpignn_v2_source_removed: met; ΔMAE -0.070458 CI [-0.118491,-0.021909]; ΔR² +0.011467 CI [+0.007275,+0.016708].
h=6, C vs stpignn_v2_transport_removed: not met; ΔMAE +0.542288 CI [+0.148045,+0.908441]; ΔR² -0.048384 CI [-0.081291,-0.011246].
h=6, C vs stpignn_lambda0: not met; ΔMAE +1.470504 CI [+1.104684,+1.830290]; ΔR² -0.090921 CI [-0.127070,-0.050522].
h=6, C vs stpignn_laplacian: not met; ΔMAE +1.511716 CI [+1.165195,+1.862495]; ΔR² -0.109973 CI [-0.141105,-0.082022].

Any-model win: met.
C physics-in-architecture support: not met.
DEM criterion: not assessed.
