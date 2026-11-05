# Benchmark v2g

Source `scripts/summarize_benchmark_v2j.py`, `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], commit `94e09d8b3b7578309dfc6a022e3ec3e899d4c0e5`, 2026-11-05T16:08:43.502072+00:00.

| h (hours) | Model | Test pairs | MAE (µg/m³) | R² |
|---:|---|---:|---:|---:|
| 1 | adaptive_graph_st | 14583 | 7.946646 | 0.589726 |
| 1 | adaptive_graph_st_fixed_knn | 14583 | 8.133109 | 0.583399 |
| 1 | climatology_hod_dow | 14583 | 21.468647 | -0.092450 |
| 1 | gine_gru_wind | 14583 | 7.983870 | 0.576905 |
| 1 | gru_only | 14583 | 7.991347 | 0.577336 |
| 1 | persistence | 14583 | 8.116095 | 0.532089 |
| 1 | ridge_lag_calendar_weather | 14583 | 8.706329 | 0.569749 |
| 1 | same_hour_yesterday | 14583 | 14.130312 | 0.283173 |
| 1 | st_gru_gcn | 14583 | 8.219692 | 0.546568 |
| 1 | station_train_mean | 14583 | 20.964647 | -0.014396 |
| 1 | stpignn_lambda0 | 14583 | 8.052157 | 0.577463 |
| 1 | stpignn_laplacian | 14583 | 8.098208 | 0.584650 |
| 1 | stpignn_original | 14583 | 8.025685 | 0.584580 |
| 1 | stpignn_v2 | 14583 | 9.529689 | 0.525801 |
| 1 | stpignn_v2_source_removed | 14583 | 9.520366 | 0.521431 |
| 1 | stpignn_v2_transport_removed | 14583 | 8.071176 | 0.571929 |
| 1 | vanilla_gcn | 14583 | 8.255069 | 0.539090 |
| 3 | adaptive_graph_st | 14583 | 13.052213 | 0.129641 |
| 3 | adaptive_graph_st_fixed_knn | 14583 | 12.648611 | 0.268449 |
| 3 | climatology_hod_dow | 14583 | 21.468647 | -0.092450 |
| 3 | gine_gru_wind | 14583 | 12.744374 | 0.280456 |
| 3 | gru_only | 14583 | 12.654972 | 0.259475 |
| 3 | persistence | 14583 | 13.244358 | 0.100938 |
| 3 | ridge_lag_calendar_weather | 14583 | 13.356836 | 0.313913 |
| 3 | same_hour_yesterday | 14583 | 14.130312 | 0.283173 |
| 3 | st_gru_gcn | 14583 | 13.172390 | 0.146772 |
| 3 | station_train_mean | 14583 | 20.964647 | -0.014396 |
| 3 | stpignn_lambda0 | 14583 | 12.471519 | 0.278184 |
| 3 | stpignn_laplacian | 14583 | 12.164030 | 0.312659 |
| 3 | stpignn_original | 14583 | 12.341537 | 0.304991 |
| 3 | stpignn_v2 | 14583 | 13.321236 | 0.225775 |
| 3 | stpignn_v2_source_removed | 14583 | 13.542488 | 0.207820 |
| 3 | stpignn_v2_transport_removed | 14583 | 13.181196 | 0.274787 |
| 3 | vanilla_gcn | 14583 | 13.230824 | 0.135705 |
| 6 | adaptive_graph_st | 14583 | 15.171126 | 0.097414 |
| 6 | adaptive_graph_st_fixed_knn | 14583 | 15.955085 | 0.068961 |
| 6 | climatology_hod_dow | 14583 | 21.468647 | -0.092450 |
| 6 | gine_gru_wind | 14583 | 16.025676 | 0.121780 |
| 6 | gru_only | 14583 | 15.162159 | 0.110641 |
| 6 | persistence | 14583 | 16.606891 | -0.161368 |
| 6 | ridge_lag_calendar_weather | 14583 | 16.106333 | 0.171015 |
| 6 | same_hour_yesterday | 14583 | 14.130312 | 0.283173 |
| 6 | st_gru_gcn | 14583 | 16.467860 | -0.103882 |
| 6 | station_train_mean | 14583 | 20.964647 | -0.014396 |
| 6 | stpignn_lambda0 | 14583 | 15.116481 | 0.142052 |
| 6 | stpignn_laplacian | 14583 | 14.835915 | 0.171044 |
| 6 | stpignn_original | 14583 | 14.706262 | 0.181031 |
| 6 | stpignn_v2 | 14583 | 15.855576 | 0.095351 |
| 6 | stpignn_v2_source_removed | 14583 | 16.025538 | 0.063317 |
| 6 | stpignn_v2_transport_removed | 14583 | 15.878058 | 0.126021 |
| 6 | vanilla_gcn | 14583 | 16.611604 | -0.113498 |
| 12 | adaptive_graph_st | 14583 | 16.926308 | -0.007270 |
| 12 | adaptive_graph_st_fixed_knn | 14583 | 17.601434 | -0.059712 |
| 12 | climatology_hod_dow | 14583 | 21.468647 | -0.092450 |
| 12 | gine_gru_wind | 14583 | 16.876650 | 0.080042 |
| 12 | gru_only | 14583 | 16.388554 | 0.068118 |
| 12 | persistence | 14583 | 19.105561 | -0.456901 |
| 12 | ridge_lag_calendar_weather | 14583 | 17.389648 | 0.084610 |
| 12 | same_hour_yesterday | 14583 | 14.130312 | 0.283173 |
| 12 | st_gru_gcn | 14583 | 19.540140 | -0.328535 |
| 12 | station_train_mean | 14583 | 20.964647 | -0.014396 |
| 12 | stpignn_lambda0 | 14583 | 15.771677 | 0.104603 |
| 12 | stpignn_laplacian | 14583 | 15.506682 | 0.179835 |
| 12 | stpignn_original | 14583 | 15.509281 | 0.142016 |
| 12 | stpignn_v2 | 14583 | 17.663727 | -0.000258 |
| 12 | stpignn_v2_source_removed | 14583 | 18.237435 | -0.107369 |
| 12 | stpignn_v2_transport_removed | 14583 | 17.490540 | 0.035421 |
| 12 | vanilla_gcn | 14583 | 19.054571 | -0.417399 |
| 24 | adaptive_graph_st | 14583 | 13.744016 | 0.396024 |
| 24 | adaptive_graph_st_fixed_knn | 14583 | 15.171014 | 0.353674 |
| 24 | climatology_hod_dow | 14583 | 21.468647 | -0.092450 |
| 24 | gine_gru_wind | 14583 | 14.188251 | 0.390879 |
| 24 | gru_only | 14583 | 14.106813 | 0.372422 |
| 24 | persistence | 14583 | 14.130312 | 0.283173 |
| 24 | ridge_lag_calendar_weather | 14583 | 15.005095 | 0.357805 |
| 24 | same_hour_yesterday | 14583 | 14.130312 | 0.283173 |
| 24 | st_gru_gcn | 14583 | 13.896435 | 0.329070 |
| 24 | station_train_mean | 14583 | 20.964647 | -0.014396 |
| 24 | stpignn_lambda0 | 14583 | 13.756937 | 0.379094 |
| 24 | stpignn_laplacian | 14583 | 14.004429 | 0.380395 |
| 24 | stpignn_original | 14583 | 13.901807 | 0.377261 |
| 24 | stpignn_v2 | 14583 | 14.708729 | 0.344348 |
| 24 | stpignn_v2_source_removed | 14583 | 14.677748 | 0.343028 |
| 24 | stpignn_v2_transport_removed | 14583 | 14.044759 | 0.384829 |
| 24 | vanilla_gcn | 14583 | 14.028811 | 0.329959 |

## Fixed criteria

h=1, gine_gru_wind: met; persistence ΔMAE -0.132225 CI [-0.216927,-0.052045]; same_hour_yesterday ΔMAE -6.146442 CI [-6.900165,-5.419064].
h=1, adaptive_graph_st: met; persistence ΔMAE -0.169449 CI [-0.284212,-0.053512]; same_hour_yesterday ΔMAE -6.183665 CI [-6.925528,-5.438952].
h=1, adaptive_graph_st_fixed_knn: not met; persistence ΔMAE +0.017014 CI [-0.103356,+0.138057]; same_hour_yesterday ΔMAE -5.997203 CI [-6.747396,-5.252284].
h=1, stpignn_v2: not met; persistence ΔMAE +1.413594 CI [+1.145301,+1.694451]; same_hour_yesterday ΔMAE -4.600623 CI [-5.403371,-3.830316].
h=1, stpignn_v2_source_removed: not met; persistence ΔMAE +1.404270 CI [+1.127552,+1.689757]; same_hour_yesterday ΔMAE -4.609946 CI [-5.419543,-3.838364].
h=1, stpignn_v2_transport_removed: not met; persistence ΔMAE -0.044919 CI [-0.135443,+0.042624]; same_hour_yesterday ΔMAE -6.059135 CI [-6.817997,-5.325371].
h=1, gru_only: met; persistence ΔMAE -0.124748 CI [-0.211269,-0.041825]; same_hour_yesterday ΔMAE -6.138964 CI [-6.891419,-5.400934].
h=1, vanilla_gcn: not met; persistence ΔMAE +0.138973 CI [+0.097528,+0.183047]; same_hour_yesterday ΔMAE -5.875243 CI [-6.655790,-5.108555].
h=1, st_gru_gcn: not met; persistence ΔMAE +0.103597 CI [+0.061070,+0.146453]; same_hour_yesterday ΔMAE -5.910619 CI [-6.676339,-5.157949].
h=1, stpignn_original: not met; persistence ΔMAE -0.090410 CI [-0.189909,+0.002105]; same_hour_yesterday ΔMAE -6.104627 CI [-6.863391,-5.357383].
h=1, stpignn_lambda0: not met; persistence ΔMAE -0.063938 CI [-0.144829,+0.018536]; same_hour_yesterday ΔMAE -6.078155 CI [-6.839228,-5.336821].
h=1, stpignn_laplacian: not met; persistence ΔMAE -0.017887 CI [-0.122860,+0.086231]; same_hour_yesterday ΔMAE -6.032104 CI [-6.788533,-5.292411].
h=3, gine_gru_wind: met; persistence ΔMAE -0.499984 CI [-0.825387,-0.200345]; same_hour_yesterday ΔMAE -1.385938 CI [-2.230282,-0.596680].
h=3, adaptive_graph_st: met; persistence ΔMAE -0.192145 CI [-0.231856,-0.156555]; same_hour_yesterday ΔMAE -1.078098 CI [-1.984434,-0.212886].
h=3, adaptive_graph_st_fixed_knn: met; persistence ΔMAE -0.595747 CI [-0.910680,-0.289615]; same_hour_yesterday ΔMAE -1.481701 CI [-2.313348,-0.685956].
h=3, stpignn_v2: not met; persistence ΔMAE +0.076878 CI [-0.281714,+0.444019]; same_hour_yesterday ΔMAE -0.809076 CI [-1.731380,+0.063590].
h=3, stpignn_v2_source_removed: not met; persistence ΔMAE +0.298130 CI [-0.025239,+0.634577]; same_hour_yesterday ΔMAE -0.587824 CI [-1.532187,+0.311045].
h=3, stpignn_v2_transport_removed: not met; persistence ΔMAE -0.063163 CI [-0.408680,+0.280036]; same_hour_yesterday ΔMAE -0.949116 CI [-1.803652,-0.161251].
h=3, gru_only: met; persistence ΔMAE -0.589387 CI [-0.924661,-0.271241]; same_hour_yesterday ΔMAE -1.475340 CI [-2.314517,-0.660370].
h=3, vanilla_gcn: not met; persistence ΔMAE -0.013534 CI [-0.106315,+0.080217]; same_hour_yesterday ΔMAE -0.899488 CI [-1.825080,-0.027127].
h=3, st_gru_gcn: not met; persistence ΔMAE -0.071968 CI [-0.150420,+0.004393]; same_hour_yesterday ΔMAE -0.957922 CI [-1.883724,-0.093732].
h=3, stpignn_original: met; persistence ΔMAE -0.902821 CI [-1.217034,-0.595843]; same_hour_yesterday ΔMAE -1.788775 CI [-2.629511,-1.007196].
h=3, stpignn_lambda0: met; persistence ΔMAE -0.772839 CI [-1.112657,-0.448616]; same_hour_yesterday ΔMAE -1.658792 CI [-2.495622,-0.861187].
h=3, stpignn_laplacian: met; persistence ΔMAE -1.080328 CI [-1.383569,-0.798276]; same_hour_yesterday ΔMAE -1.966281 CI [-2.791331,-1.185205].
h=6, gine_gru_wind: not met; persistence ΔMAE -0.581216 CI [-1.059127,-0.113383]; same_hour_yesterday ΔMAE +1.895364 CI [+1.082542,+2.734533].
h=6, adaptive_graph_st: not met; persistence ΔMAE -1.435765 CI [-1.857324,-0.975265]; same_hour_yesterday ΔMAE +1.040814 CI [+0.210452,+1.903569].
h=6, adaptive_graph_st_fixed_knn: not met; persistence ΔMAE -0.651806 CI [-1.096844,-0.207865]; same_hour_yesterday ΔMAE +1.824774 CI [+0.957738,+2.694820].
h=6, stpignn_v2: not met; persistence ΔMAE -0.751315 CI [-1.256808,-0.271716]; same_hour_yesterday ΔMAE +1.725264 CI [+0.833057,+2.640829].
h=6, stpignn_v2_source_removed: not met; persistence ΔMAE -0.581354 CI [-0.985350,-0.188730]; same_hour_yesterday ΔMAE +1.895226 CI [+0.990012,+2.813658].
h=6, stpignn_v2_transport_removed: not met; persistence ΔMAE -0.728833 CI [-1.210679,-0.252709]; same_hour_yesterday ΔMAE +1.747746 CI [+0.936035,+2.575977].
h=6, gru_only: not met; persistence ΔMAE -1.444732 CI [-1.880504,-1.003683]; same_hour_yesterday ΔMAE +1.031848 CI [+0.219547,+1.876354].
h=6, vanilla_gcn: not met; persistence ΔMAE +0.004713 CI [-0.148699,+0.165737]; same_hour_yesterday ΔMAE +2.481292 CI [+1.525441,+3.455021].
h=6, st_gru_gcn: not met; persistence ΔMAE -0.139031 CI [-0.266578,-0.012351]; same_hour_yesterday ΔMAE +2.337548 CI [+1.381642,+3.301297].
h=6, stpignn_original: not met; persistence ΔMAE -1.900629 CI [-2.343760,-1.441736]; same_hour_yesterday ΔMAE +0.575950 CI [-0.212747,+1.373650].
h=6, stpignn_lambda0: not met; persistence ΔMAE -1.490410 CI [-1.963357,-0.987453]; same_hour_yesterday ΔMAE +0.986169 CI [+0.167854,+1.814027].
h=6, stpignn_laplacian: not met; persistence ΔMAE -1.770976 CI [-2.232748,-1.298909]; same_hour_yesterday ΔMAE +0.705604 CI [-0.085667,+1.510486].
h=12, gine_gru_wind: not met; persistence ΔMAE -2.228911 CI [-2.953846,-1.469566]; same_hour_yesterday ΔMAE +2.746339 CI [+1.885032,+3.606532].
h=12, adaptive_graph_st: not met; persistence ΔMAE -2.179253 CI [-2.646397,-1.679069]; same_hour_yesterday ΔMAE +2.795997 CI [+1.896454,+3.743806].
h=12, adaptive_graph_st_fixed_knn: not met; persistence ΔMAE -1.504128 CI [-1.935881,-1.050168]; same_hour_yesterday ΔMAE +3.471122 CI [+2.554979,+4.463626].
h=12, stpignn_v2: not met; persistence ΔMAE -1.441834 CI [-2.017083,-0.852254]; same_hour_yesterday ΔMAE +3.533416 CI [+2.621618,+4.496355].
h=12, stpignn_v2_source_removed: not met; persistence ΔMAE -0.868127 CI [-1.340201,-0.392048]; same_hour_yesterday ΔMAE +4.107123 CI [+3.129469,+5.161717].
h=12, stpignn_v2_transport_removed: not met; persistence ΔMAE -1.615021 CI [-2.242399,-0.958637]; same_hour_yesterday ΔMAE +3.360228 CI [+2.478345,+4.245695].
h=12, gru_only: not met; persistence ΔMAE -2.717007 CI [-3.286969,-2.114294]; same_hour_yesterday ΔMAE +2.258242 CI [+1.409834,+3.126648].
h=12, vanilla_gcn: not met; persistence ΔMAE -0.050990 CI [-0.235234,+0.139631]; same_hour_yesterday ΔMAE +4.924260 CI [+3.755909,+6.212725].
h=12, st_gru_gcn: not met; persistence ΔMAE +0.434579 CI [+0.058790,+0.797067]; same_hour_yesterday ΔMAE +5.409829 CI [+4.190404,+6.669702].
h=12, stpignn_original: not met; persistence ΔMAE -3.596280 CI [-4.300959,-2.858951]; same_hour_yesterday ΔMAE +1.378969 CI [+0.590573,+2.155164].
h=12, stpignn_lambda0: not met; persistence ΔMAE -3.333884 CI [-4.061435,-2.570646]; same_hour_yesterday ΔMAE +1.641366 CI [+0.806613,+2.476607].
h=12, stpignn_laplacian: not met; persistence ΔMAE -3.598879 CI [-4.404913,-2.805783]; same_hour_yesterday ΔMAE +1.376370 CI [+0.595384,+2.133770].
h=24, gine_gru_wind: not met; persistence ΔMAE +0.057939 CI [-0.307619,+0.409348]; same_hour_yesterday ΔMAE +0.057939 CI [-0.307619,+0.409348].
h=24, adaptive_graph_st: met; persistence ΔMAE -0.386295 CI [-0.723199,-0.079855]; same_hour_yesterday ΔMAE -0.386295 CI [-0.723199,-0.079855].
h=24, adaptive_graph_st_fixed_knn: not met; persistence ΔMAE +1.040702 CI [+0.460728,+1.588534]; same_hour_yesterday ΔMAE +1.040702 CI [+0.460728,+1.588534].
h=24, stpignn_v2: not met; persistence ΔMAE +0.578417 CI [+0.081838,+1.048287]; same_hour_yesterday ΔMAE +0.578417 CI [+0.081838,+1.048287].
h=24, stpignn_v2_source_removed: not met; persistence ΔMAE +0.547436 CI [+0.073396,+1.002773]; same_hour_yesterday ΔMAE +0.547436 CI [+0.073396,+1.002773].
h=24, stpignn_v2_transport_removed: not met; persistence ΔMAE -0.085553 CI [-0.409155,+0.232846]; same_hour_yesterday ΔMAE -0.085553 CI [-0.409155,+0.232846].
h=24, gru_only: not met; persistence ΔMAE -0.023499 CI [-0.466097,+0.410028]; same_hour_yesterday ΔMAE -0.023499 CI [-0.466097,+0.410028].
h=24, vanilla_gcn: not met; persistence ΔMAE -0.101501 CI [-0.271530,+0.062929]; same_hour_yesterday ΔMAE -0.101501 CI [-0.271530,+0.062929].
h=24, st_gru_gcn: met; persistence ΔMAE -0.233876 CI [-0.349351,-0.123223]; same_hour_yesterday ΔMAE -0.233876 CI [-0.349351,-0.123223].
h=24, stpignn_original: not met; persistence ΔMAE -0.228504 CI [-0.710430,+0.239909]; same_hour_yesterday ΔMAE -0.228504 CI [-0.710430,+0.239909].
h=24, stpignn_lambda0: not met; persistence ΔMAE -0.373374 CI [-0.793311,+0.021527]; same_hour_yesterday ΔMAE -0.373374 CI [-0.793311,+0.021527].
h=24, stpignn_laplacian: not met; persistence ΔMAE -0.125883 CI [-0.618065,+0.353246]; same_hour_yesterday ΔMAE -0.125883 CI [-0.618065,+0.353246].

Any-model win: met.
Physics criterion: see fixed lambda check h=1 and h=24.
DEM criterion: not met.
